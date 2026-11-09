import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing_observation import (
    ObservationLimits, TagObservation, ObservationGate)


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.limits = ObservationLimits(.2, 2., .04, .1, 3.)
        self.gate = ObservationGate(7, 'down', 'fixture-v1', self.limits)
        self.o = TagObservation(7, 'down', 'fixture-v1', 10., (0., 0., 1.), 1., .01)

    def test_valid_snapshot_is_immutable_copy(self):
        pose = [0., 0., 1.]
        decision = self.gate.evaluate(replace(self.o, position_m=pose), 10.)
        pose[2] = 99
        self.assertTrue(decision.accepted)
        self.assertEqual(decision.position_m, (0., 0., 1.))

    def test_v01_stale_boundary_and_future_clock(self):
        self.assertTrue(self.gate.evaluate(self.o, 10.2).accepted)
        self.assertEqual(self.gate.evaluate(self.o, 10.201).reason, 'stale')
        self.assertEqual(self.gate.evaluate(self.o, 9.).reason, 'invalid_receive_time')
        for now in (True, float('nan'), float('inf'), -1, '10'):
            self.assertFalse(self.gate.evaluate(self.o, now).accepted)

    def test_v02_identity_and_boolean_id(self):
        for field, value, reason in (
                ('tag_id', 8, 'wrong_tag'), ('tag_id', True, 'wrong_tag'),
                ('camera_id', 'front', 'wrong_camera'),
                ('calibration_id', 'old', 'wrong_calibration')):
            with self.subTest(field=field, value=value):
                self.assertEqual(self.gate.evaluate(replace(self.o, **{field: value}), 10.).reason,
                                 reason)

    def test_v03_nonfinite_and_wrong_dimension_pose(self):
        for pose in (None, (), (1, 2), (1, 2, 3, 4), (True, 0, 1),
                     (float('nan'), 0, 1), (0, 0, float('inf')), (10**1000, 0, 1)):
            with self.subTest(pose=repr(pose)[:40]):
                self.assertEqual(self.gate.evaluate(replace(self.o, position_m=pose), 10.).reason,
                                 'invalid_position')

    def test_v04_quality_metrics_cannot_be_truthy_or_negative(self):
        for field in ('reprojection_px', 'position_sigma_m'):
            for value in (True, '0', -1., float('nan'), float('inf')):
                with self.subTest(field=field, value=value):
                    self.assertFalse(self.gate.evaluate(replace(self.o, **{field: value}), 10.).accepted)
        self.assertEqual(self.gate.evaluate(replace(self.o, reprojection_px=2.01), 10.).reason,
                         'reprojection_too_high')
        self.assertEqual(self.gate.evaluate(replace(self.o, position_sigma_m=.041), 10.).reason,
                         'uncertainty_too_high')

    def test_v05_depth_envelope_is_inclusive(self):
        for depth in (.1, 3.):
            self.assertTrue(self.gate.evaluate(replace(self.o, position_m=(0, 0, depth)), 10.).accepted)
        for depth in (0., -.1, .099, 3.001):
            self.assertEqual(self.gate.evaluate(replace(self.o, position_m=(0, 0, depth)), 10.).reason,
                             'depth_outside_experiment')

    def test_invalid_limits_and_identity(self):
        for values in ((0, 2, .04, .1, 3), (.2, 2, .04, 3, .1),
                       (True, 2, .04, .1, 3), (.2, float('inf'), .04, .1, 3)):
            with self.assertRaises(ValueError):
                ObservationLimits(*values)
        for args in ((True, 'down', 'v1'), (-1, 'down', 'v1'),
                     (7, '', 'v1'), (7, ' down', 'v1')):
            with self.assertRaises(ValueError):
                ObservationGate(*args, self.limits)

    def test_missing_observation_is_not_valid_pose(self):
        self.assertEqual(self.gate.evaluate(None, 10.).reason, 'missing_observation')
        self.assertFalse(self.gate.evaluate({}, 10.).accepted)
