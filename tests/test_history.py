import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.history import TelemetryHistory


class HistoryTests(unittest.TestCase):
    def test_bounded_snapshot_and_copy(self):
        h = TelemetryHistory(2)
        self.assertIsNone(h.snapshot(0)['age'])
        for text in ('one', 'two', 'three'):
            h.ack(text)
        h.update('LOITER', 90, False, 1)
        snapshot = h.snapshot(2)
        self.assertEqual(snapshot['acks'], ['two', 'three'])
        self.assertEqual(snapshot['age'], 1)
        snapshot['acks'].clear()
        self.assertEqual(len(h.snapshot(2)['acks']), 2)
        with self.assertRaises(ValueError):
            h.snapshot(1)
