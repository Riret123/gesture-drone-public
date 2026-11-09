import unittest
from gesture_control.core_latency import LatencyLedger


class CoreLatencyTests(unittest.TestCase):
    def test_stage_budget_and_bounded_summary(self):
        ledger = LatencyLedger(max_samples=2, budget_ms=100.)
        for start, elapsed in ((0., .05), (1., .2), (2., .08)):
            self.assertTrue(ledger.record(start, start + .01,
                                          start + .03, start + elapsed))
        result = ledger.summary()
        self.assertEqual(result['samples_retained'], 2)
        self.assertEqual(result['samples_total'], 3)
        self.assertEqual(result['over_budget_total'], 1)
        self.assertAlmostEqual(result['total_ms']['max'], 200.)
        self.assertAlmostEqual(result['capture_to_inference_ms']['max'], 10.)

    def test_bad_timing_does_not_poison_summary(self):
        ledger = LatencyLedger()
        for sample in ((True, 1., 2., 3.), (2., 1., 3., 4.),
                       (0., 1., float('nan'), 3.), (0., 1., 2., '3')):
            self.assertFalse(ledger.record(*sample))
        self.assertEqual(ledger.summary()['samples_total'], 0)

    def test_config_validation(self):
        for size in (0, True, 1.5, 100001):
            with self.assertRaises(ValueError):
                LatencyLedger(max_samples=size)
        for budget in (0, True, '2', float('inf')):
            with self.assertRaises(ValueError):
                LatencyLedger(budget_ms=budget)

    def test_empty_summary_has_no_fake_zero_measurement(self):
        result = LatencyLedger().summary()
        self.assertIsNone(result['total_ms'])
