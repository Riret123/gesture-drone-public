import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import math
import unittest
from gesture_control.slew import SlewLimiter


class SlewTests(unittest.TestCase):
    def test_vector_bound_and_stop(self):
        s = SlewLimiter()
        first = s.update((1, 1), .1)
        self.assertAlmostEqual(math.hypot(*first), .03)
        for _ in range(100):
            self.assertLessEqual(math.hypot(*s.update((1, 1), .1)), .2000001)
        self.assertEqual(s.update((1, 1), .1, stop=True), (0, 0))
        with self.assertRaises(ValueError):
            s.update((1, 1), 2)
