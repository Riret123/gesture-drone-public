"""Recorded Windows fixture timings validate accounting, not Orange Pi throughput."""
import unittest
from gesture_control.core_latency import LatencyLedger


class MeasuredFixtureLatencyTests(unittest.TestCase):
    def test_recorded_classification_sample_and_reviewed_budget(self):
        # tools/benchmark_core.py --repeats 100, Windows AMD64, 2026-11-09.
        # Real perf_counter sample; excludes camera and MediaPipe inference.
        measured = (406484.1562184, 406484.1562188,
                    406484.1562883, 406484.1562886)
        ledger = LatencyLedger(budget_ms=100.)
        self.assertTrue(ledger.record(*measured))
        summary = ledger.summary()
        self.assertEqual(summary['samples_total'], 1)
        self.assertEqual(summary['over_budget_total'], 0)
        self.assertAlmostEqual(summary['total_ms']['max'], .0702, places=4)
        self.assertGreater(summary['inference_ms']['max'], 0)
        # The historical fixture cannot prove today's runtime stays within budget.
