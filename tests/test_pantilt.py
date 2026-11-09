import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.pantilt import PanTilt


class PanTiltTests(unittest.TestCase):
    def test_smoothing_and_limits(self):
        p = PanTilt()
        self.assertEqual(p.update(1, 0), (102, 78))
        for _ in range(200):
            angles = p.update(2, -1)
        self.assertTrue(all(30 <= a <= 150 for a in angles))
        self.assertEqual(p.update(float('nan'), 0), angles)
        with self.assertRaises(ValueError):
            PanTilt(alpha=0)
