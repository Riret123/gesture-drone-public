import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.energy_budget import RailLoad, evaluate_budget


class EnergyTests(unittest.TestCase):
    def test_known_budget_and_efficiency_loss(self):
        result = evaluate_budget([RailLoad('compute', 5., 2., 3., .8)], 10., 2., 3.)
        self.assertEqual(result.status, 'WITHIN_ARITHMETIC_LIMITS')
        self.assertAlmostEqual(result.continuous_w, 12.5)
        self.assertAlmostEqual(result.peak_w, 18.75)
        self.assertAlmostEqual(result.continuous_source_a, 1.25)

    def test_e03_simultaneous_peaks_are_not_averaged(self):
        loads = [RailLoad('left', 10., 1., 5., 1.), RailLoad('right', 10., 1., 5., 1.)]
        result = evaluate_budget(loads, 10., 3., 6.)
        self.assertEqual(result.peak_source_a, 10.)
        self.assertEqual(result.reasons, ('peak_capacity_exceeded',))

    def test_e06_unknown_values_never_create_passing_budget(self):
        result = evaluate_budget([RailLoad('unknown', None, None, None, None)], 10., 2., 3.)
        self.assertEqual(result.status, 'UNKNOWN')
        self.assertEqual(result.unknown_loads, ('unknown',))
        self.assertIsNone(result.continuous_w)
        result = evaluate_budget([RailLoad('a', 5, 1, 2, 1)], None, 2, 3)
        self.assertEqual(result.status, 'UNKNOWN')
        self.assertIn('missing_source_evidence', result.reasons)

    def test_invalid_load_values(self):
        for value in (0, -1, True, '5', float('nan'), float('inf'), 10**1000):
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                RailLoad('a', value, 1., 2., .9)
        for args in (('a', 5, 2, 1, 1), ('a', 5, 1, 2, 1.01), (' ', 5, 1, 2, 1)):
            with self.assertRaises(ValueError):
                RailLoad(*args)

    def test_duplicate_empty_or_unvalidated_load_list_rejects(self):
        load = RailLoad('a', 5, 1, 2, 1)
        for loads in ([], [load, load], [{}], None):
            with self.assertRaises(ValueError):
                evaluate_budget(loads, 10, 2, 3)

    def test_source_values_and_peak_order(self):
        load = RailLoad('a', 5, 1, 2, 1)
        for source in ((0, 2, 3), (True, 2, 3), (10, 3, 2), (10, float('nan'), 3)):
            with self.assertRaises(ValueError):
                evaluate_budget([load], *source)

    def test_continuous_and_peak_capacity_reasons(self):
        result = evaluate_budget([RailLoad('a', 10, 3, 5, 1)], 10, 2, 4)
        self.assertEqual(result.status, 'EXCEEDS')
        self.assertEqual(result.reasons, ('continuous_capacity_exceeded', 'peak_capacity_exceeded'))

    def test_boundary_and_overflow(self):
        result = evaluate_budget([RailLoad('a', 10, 2, 4, 1)], 10, 2, 4)
        self.assertEqual(result.status, 'WITHIN_ARITHMETIC_LIMITS')
        huge = RailLoad('huge', 1e308, 1e308, 1e308, 1)
        self.assertEqual(evaluate_budget([huge], 1, 2, 3).status, 'INVALID')

    def test_e25_scalar_underflow_does_not_pass_as_zero_demand(self):
        tiny = RailLoad('tiny', 1e-300, 1e-300, 1e-300, 1)
        result = evaluate_budget([tiny], 1, 1, 1)
        self.assertEqual(result.status, 'INVALID')
        self.assertEqual(result.reasons, ('arithmetic_underflow',))
        tiny_current = RailLoad('tiny', 1e-200, 1, 1, 1)
        result = evaluate_budget([tiny_current], 1e200, 1, 1)
        self.assertEqual(result.reasons, ('arithmetic_underflow',))
