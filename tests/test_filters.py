import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.filters import EMA, OneEuro


class FilterTests(unittest.TestCase):
    def test_ema(self):
        f = EMA(.5)
        self.assertEqual(f.update(0), 0)
        self.assertEqual(f.update(1), .5)
        with self.assertRaises(ValueError):
            f.update(float('nan'))

    def test_euro(self):
        f = OneEuro()
        self.assertEqual(f.update(0, 0), 0)
        self.assertTrue(0 < f.update(1, .1) < 1)
        with self.assertRaises(ValueError):
            f.update(1, .1)
        with self.assertRaises(ValueError):
            OneEuro(min_cutoff=0)
