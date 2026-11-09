import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import math
import unittest
from gesture_control.velocity import hand_velocity


class VelocityTests(unittest.TestCase):
    def test_enable_center_limit(self):
        self.assertEqual(hand_velocity(1, 1), (0, 0))
        self.assertEqual(hand_velocity(.51, .49, True), (0, 0))
        self.assertLessEqual(math.hypot(*hand_velocity(1, 1, True)), .2)
        self.assertLess(hand_velocity(0, .5, True)[0], 0)
        self.assertEqual(hand_velocity(float('nan'), 0, True), (0, 0))
