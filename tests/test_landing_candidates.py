import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing_observation import ObservationGate, ObservationLimits, TagObservation
from gesture_control.landing_capture import CaptureGate
from gesture_control.landing_candidates import CandidateFrame, CandidateGate


class CandidateTests(unittest.TestCase):
    def setUp(self):
        meta = ObservationGate(7, 'down', 'v1', ObservationLimits(.2, 2, .04, .1, 3))
        self.gate = CandidateGate(CaptureGate(meta, 'a', .3), 3)
        self.o = TagObservation(7, 'down', 'v1', 1., (0, 0, 1), 1., .01)
        self.frame = CandidateFrame('a', 0, .9, (self.o,))

    def test_one_target_with_other_tags_accepts(self):
        other = replace(self.o, tag_id=8)
        result = self.gate.evaluate(replace(self.frame, candidates=(other, self.o)), 1.)
        self.assertTrue(result.accepted)

    def test_v15_duplicate_target_rejects_even_if_identical(self):
        for duplicate in (self.o, replace(self.o, position_m=(1, 0, 1))):
            self.assertEqual(self.gate.evaluate(replace(self.frame, candidates=(self.o, duplicate)), 1.).reason,
                             'target_ambiguous')
        self.assertTrue(self.gate.evaluate(self.frame, 1.).accepted)

    def test_bounded_before_candidate_validation(self):
        frame = replace(self.frame, candidates=(None,) * 4)
        self.assertEqual(self.gate.evaluate(frame, 1.).reason, 'too_many_candidates')

    def test_mixed_camera_calibration_and_receive_reject(self):
        for field, value, reason in (
                ('camera_id', 'front', 'mixed_camera_frame'),
                ('calibration_id', 'old', 'mixed_calibration_frame'),
                ('received_s', .99, 'mixed_receive_times')):
            other = replace(self.o, tag_id=8, **{field: value})
            self.assertEqual(self.gate.evaluate(replace(self.frame, candidates=(self.o, other)), 1.).reason,
                             reason)

    def test_absent_target_does_not_consume_sequence(self):
        self.assertEqual(self.gate.evaluate(replace(self.frame, candidates=()), 1.).reason, 'target_absent')
        self.assertTrue(self.gate.evaluate(self.frame, 1.).accepted)

    def test_selected_pose_still_needs_quality_and_capture_validation(self):
        bad = replace(self.o, reprojection_px=9)
        self.assertEqual(self.gate.evaluate(replace(self.frame, candidates=(bad,)), 1.).reason,
                         'reprojection_too_high')
        self.assertTrue(self.gate.evaluate(self.frame, 1.).accepted)
        self.assertEqual(self.gate.evaluate(self.frame, 1.).reason, 'replayed_or_reordered')

    def test_malformed_container_candidate_and_boolean_id(self):
        for frame, reason in ((None, 'missing_frame'),
                              (replace(self.frame, candidates=[]), 'invalid_candidate_container'),
                              (replace(self.frame, candidates=(None,)), 'invalid_candidate'),
                              (replace(self.frame, candidates=(replace(self.o, tag_id=True),)),
                               'invalid_candidate_id')):
            self.assertEqual(self.gate.evaluate(frame, 1.).reason, reason)

    def test_invalid_candidate_bound(self):
        for count in (True, 0, -1, 1., '3'):
            with self.assertRaises(ValueError):
                CandidateGate(self.gate.capture_gate, count)

    def test_v21_invalid_first_distractor_receive_time_never_acts_as_sentinel(self):
        for value in (None, True, float('nan'), float('inf'), -1):
            distractor = replace(self.o, tag_id=8, received_s=value)
            frame = replace(self.frame, candidates=(distractor, self.o))
            self.assertEqual(self.gate.evaluate(frame, 1.).reason, 'invalid_candidate_receive_time')
        self.assertTrue(self.gate.evaluate(self.frame, 1.).accepted)

    def test_v22_rejected_frame_still_advances_receiver_clock(self):
        self.assertEqual(self.gate.evaluate(None, 2.).reason, 'missing_frame')
        self.assertEqual(self.gate.evaluate(self.frame, 1.).reason, 'clock_reversed')
        self.assertEqual(self.gate.evaluate(self.frame, True).reason, 'invalid_clock')
