import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.battery import BatteryPolicy


class BatteryTests(unittest.TestCase):
    def test_hysteresis(self):
        b = BatteryPolicy()
        self.assertEqual(b.update(14.0, 4), 'rtl')
        self.assertEqual(b.update(14.4, 4), 'rtl')
        self.assertEqual(b.update(15.0, 4), 'allow')
        self.assertEqual(b.update(13.0, 4), 'land')
        self.assertEqual(b.update(13.4, 4), 'land')
        self.assertEqual(b.update(14.0, 4), 'rtl')
        self.assertEqual(b.update(float('nan'), 4), 'hold')
        self.assertEqual(b.update(14, 0), 'hold')
        with self.assertRaises(ValueError):
            BatteryPolicy(low=3, critical=4)
