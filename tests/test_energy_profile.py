import sys
from pathlib import Path
import unittest
from functools import partial

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.energy_profile import CurrentSegment, evaluate_profile as _evaluate_profile

evaluate_profile = partial(_evaluate_profile, max_segments=16)


class ProfileTests(unittest.TestCase):
    def test_e11_same_peak_different_duration_changes_energy(self):
        short = evaluate_profile([CurrentSegment(1, 2)], 10, 3, 3, 100)
        long = evaluate_profile([CurrentSegment(10, 2)], 10, 3, 3, 100)
        self.assertEqual(short.peak_a, long.peak_a)
        self.assertEqual(short.energy_j, 20)
        self.assertEqual(long.energy_j, 200)
        self.assertEqual(long.reasons, ('energy_exceeded',))

    def test_rms_includes_known_zero_idle(self):
        result = evaluate_profile([CurrentSegment(1, 2), CurrentSegment(3, 0)], 10, 2, 1, 20)
        self.assertEqual(result.duration_s, 4)
        self.assertEqual(result.rms_a, 1)
        self.assertEqual(result.status, 'WITHIN_ARITHMETIC_LIMITS')

    def test_e14_zero_known_current_differs_from_unknown(self):
        result = evaluate_profile([CurrentSegment(1, 0)], 10, 1, 1, 1)
        self.assertEqual(result.energy_j, 0)
        with self.assertRaises(ValueError):
            CurrentSegment(1, None)

    def test_regeneration_rejects_consumption_only_model(self):
        with self.assertRaises(ValueError):
            CurrentSegment(1, -1)

    def test_invalid_duration_current_and_limits(self):
        for value in (True, 0, -1, float('nan'), float('inf'), 10**1000):
            with self.assertRaises(ValueError):
                CurrentSegment(value, 1)
        for value in (True, float('nan'), float('inf'), '1'):
            with self.assertRaises(ValueError):
                CurrentSegment(1, value)
        with self.assertRaises(ValueError):
            evaluate_profile([CurrentSegment(1, 1)], 10, True, 1, 1)

    def test_empty_or_unvalidated_segments_reject(self):
        for segments in ([], [None], None):
            with self.assertRaises(ValueError):
                evaluate_profile(segments, 10, 1, 1, 1)

    def test_all_limit_reasons_and_overflow(self):
        result = evaluate_profile([CurrentSegment(10, 10)], 10, 5, 5, 5)
        self.assertEqual(result.reasons, ('peak_exceeded', 'rms_exceeded', 'energy_exceeded'))
        result = evaluate_profile([CurrentSegment(1e308, 1e308)], 10, 5, 5, 5)
        self.assertEqual(result.status, 'INVALID')

    def test_partitioning_constant_segment_preserves_result(self):
        first = evaluate_profile([CurrentSegment(4, 2)], 10, 3, 3, 100)
        split = evaluate_profile([CurrentSegment(1, 2), CurrentSegment(3, 2)], 10, 3, 3, 100)
        self.assertEqual(first, split)

    def test_e19_nonzero_load_underflow_is_invalid_not_zero_demand(self):
        result = evaluate_profile([CurrentSegment(1e-300, 1e-300)], 10, 1, 1, 1)
        self.assertEqual(result.status, 'INVALID')
        self.assertEqual(result.reasons, ('arithmetic_underflow',))
        result = evaluate_profile([CurrentSegment(1, 1e-100)], 1e-300, 1, 1, 1)
        self.assertEqual(result.reasons, ('arithmetic_underflow',))

    def test_e21_explicit_segment_bound_before_iteration(self):
        with self.assertRaisesRegex(ValueError, 'count limit exceeded'):
            _evaluate_profile([None] * 3, 10, 1, 1, 1, max_segments=2)
        for limit in (True, 0, -1, 1.):
            with self.assertRaises(ValueError):
                _evaluate_profile([CurrentSegment(1, 1)], 10, 1, 1, 1, max_segments=limit)
