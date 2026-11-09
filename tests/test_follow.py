import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.follow import PID, FollowController


class FollowTests(unittest.TestCase):
    def test_windup_and_recovery(self):
        p = PID(kp=1, ki=1, kd=0)
        for _ in range(100):
            self.assertEqual(p.update(10, .1), .2)
        self.assertEqual(p.integral, 0)
        self.assertLess(p.update(-.1, .1), 0)
        with self.assertRaises(ValueError):
            p.update(0, 0)

    def test_box_and_loss(self):
        f = FollowController()
        lateral, forward = f.update((.6, .2, .8, .4), .1)
        self.assertGreater(lateral, 0)
        self.assertGreater(forward, 0)
        self.assertEqual(f.update(None, .1), (0, 0))
        self.assertEqual(f.update((1, 1, 0, 0), .1), (0, 0))
