import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.freshness import Freshness


class FreshnessTests(unittest.TestCase):
    def test_boundaries_and_clock(self):
        f = Freshness(.25)
        self.assertFalse(f.fresh(0))
        f.receive(.1)
        self.assertTrue(f.fresh(.34))
        self.assertFalse(f.fresh(.35))
        with self.assertRaises(ValueError):
            f.receive(.2)
        with self.assertRaises(ValueError):
            f.fresh(float('nan'))
