import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src/gesture_control'), str(ROOT / 'src/drone_bringup')]
from gesture_control.safety import GestureDebouncer, GestureSafety


class SafetyTests(unittest.TestCase):
    def test_debounce(self):
        d = GestureDebouncer(2)
        self.assertIsNone(d.update('fist'))
        self.assertIsNone(d.update('open_palm'))
        self.assertEqual(d.update('open_palm'), 'open_palm')
        d.update(None)
        self.assertIsNone(d.update('open_palm'))

    def test_timeouts(self):
        s = GestureSafety(now=10)
        self.assertIsNone(s.update([], 11.99))
        self.assertEqual(s.update([], 12), 'hold')
        self.assertIsNone(s.update(['other'], 14.9))
        self.assertEqual(s.update([], 15), 'land')
        self.assertIsNone(s.update([], 16))

    def test_emergency(self):
        s = GestureSafety()
        self.assertEqual(s.update(['fist', 'fist'], 0), 'emergency')

    def test_recovery_and_noise(self):
        s = GestureSafety(2)
        s.update(['open_palm'], 1)
        self.assertEqual(s.update(['open_palm'], 1.1), 'open_palm')
        self.assertIsNone(s.update(['other'], 2))
        self.assertEqual(s.update([], 3.1), 'hold')
        self.assertIsNone(s.update(['fist'], 3.2))
        self.assertEqual(s.update(['fist'], 3.3), 'fist')
        self.assertEqual(s.update([], 8.3), 'land')

    def test_invalid_config_and_time(self):
        for n in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                GestureDebouncer(n)
        for h, l in ((0, 5), (5, 2), (2, float('nan'))):
            with self.assertRaises(ValueError):
                GestureSafety(hold_after=h, land_after=l)
        with self.assertRaises(ValueError):
            GestureSafety(now=2).update([], 1)
