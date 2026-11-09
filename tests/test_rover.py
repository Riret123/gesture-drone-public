import unittest
from gesture_control.rover import wheels, control


class RoverTests(unittest.TestCase):
    def test_kinematics(self):
        self.assertEqual(wheels(.2, 0), (.2, .2))
        left, right = wheels(0, 1)
        self.assertEqual(left, -right)
        self.assertLessEqual(max(map(abs, wheels(10, 5))), .4)
        with self.assertRaises(ValueError):
            wheels(0, 0, track=0)

    def test_modes_watchdog(self):
        self.assertEqual(control('hold', (3, 0), 0), (0, 0))
        self.assertEqual(control('follow', (3, 0), .5), (0, 0))
        self.assertEqual(control('follow', (1, 0), 0), (0, 0))
        self.assertGreater(control('return_home', (1, 0), 0)[0], 0)
        self.assertEqual(control('follow', (3, 0), -1), (0, 0))
