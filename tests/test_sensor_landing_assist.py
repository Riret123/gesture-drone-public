import sys
from pathlib import Path
from dataclasses import replace
import math
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.sensor_landing_assist import RangeFlowSample, estimate_planar_flow


class AssistTests(unittest.TestCase):
    def setUp(self):
        self.sample = RangeFlowSample(1, 2, 0, (.1, -.1), .8, True, True)
        self.limits = dict(max_age_s=.25, min_range_m=.1, max_range_m=3,
                           max_tilt_rad=.5, min_quality=.5, max_angular_flow_rps=1)

    def estimate(self, sample=None, now=1):
        return estimate_planar_flow(self.sample if sample is None else sample, now, **self.limits)

    def test_known_planar_arithmetic_without_control_output(self):
        result = self.estimate()
        self.assertEqual(result.status, 'MODEL_ESTIMATE')
        self.assertEqual(result.height_m, 2)
        self.assertEqual(result.speed_xy_mps, (.2, -.2))
        self.assertEqual(result.reason, 'unverified_planar_model')

    def test_tilt_uses_cosine_not_slant_as_height(self):
        result = self.estimate(replace(self.sample, tilt_rad=.5))
        self.assertAlmostEqual(result.height_m, 2 * math.cos(.5))

    def test_uncompensated_rotation_and_nonplanar_surface_reject(self):
        for field in ('rotation_compensated', 'planar_surface_assumed'):
            for value in (False, 1, 'yes'):
                result = self.estimate(replace(self.sample, **{field: value}))
                self.assertEqual(result.reason, 'model_preconditions_missing')
                self.assertIsNone(result.speed_xy_mps)

    def test_range_tilt_quality_and_flow_envelopes(self):
        for changes, reason in (({'slant_range_m': 4}, 'range_outside_experiment'),
                                ({'tilt_rad': .6}, 'tilt_outside_experiment'),
                                ({'quality': .4}, 'quality_too_low_or_invalid'),
                                ({'quality': True}, 'quality_too_low_or_invalid'),
                                ({'angular_flow_xy_rps': (1, 1)}, 'flow_outside_experiment'),
                                ({'angular_flow_xy_rps': (True, 0)}, 'invalid_flow')):
            self.assertEqual(self.estimate(replace(self.sample, **changes)).reason, reason)

    def test_freshness_invalid_clocks_and_missing_sample(self):
        self.assertEqual(self.estimate(now=1.25).status, 'MODEL_ESTIMATE')
        self.assertEqual(self.estimate(now=1.251).reason, 'stale')
        self.assertEqual(self.estimate(now=.9).reason, 'invalid_receive_time')
        self.assertEqual(self.estimate(now=True).reason, 'invalid_clock')
        self.assertEqual(estimate_planar_flow(None, 1, **self.limits).reason, 'missing_sample')

    def test_invalid_limits_cannot_disable_model_guards(self):
        for changes in ({'max_tilt_rad': math.pi/2}, {'min_quality': 0},
                        {'max_age_s': True}, {'min_range_m': 3}, {'max_angular_flow_rps': float('inf')}):
            with self.assertRaises(ValueError):
                estimate_planar_flow(self.sample, 1, **(self.limits | changes))
