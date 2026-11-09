import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.arbitration import Arbiter


class ArbitrationTests(unittest.TestCase):
    def test_priority_safety_and_expiry(self):
        a = Arbiter()
        a.submit('voice', 'open_palm', 0)
        a.submit('keyboard', 'hold', 0)
        self.assertEqual(a.choose(0), 'hold')
        a.submit('gesture', 'emergency', .1)
        self.assertEqual(a.choose(.1), 'emergency')
        self.assertEqual(a.choose(.6), 'hold')
        with self.assertRaises(ValueError):
            a.choose(.5)
        with self.assertRaises(ValueError):
            a.submit('unknown', 'land', 1)
