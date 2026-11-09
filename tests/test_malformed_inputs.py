import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.validation import finite
from gesture_control.landing import LandingController
from gesture_control.extended_gestures import classify
from gesture_control.protocol import encode, decode
from gesture_control.deadman import Deadman
from gesture_control.velocity import hand_velocity


class MalformedTests(unittest.TestCase):
    def test_pose_and_landmarks_fail_closed(self):
        for pose in ('abc', [True, 0, 1], [0, {}, 1], 42, (0, 0, 10**999)):
            self.assertEqual(LandingController().update(pose).state, 'abort')
        for points in (None, [None]*21, [(0, 'x')]*21):
            self.assertEqual(classify(points), 'other')
        self.assertFalse(finite(10**999))

    def test_protocol_invalid_types_and_numeric_overflow(self):
        for packet in (None, 42, 'text'):
            with self.assertRaises(ValueError):
                decode(packet)
        with self.assertRaises(ValueError):
            encode(1, 'follow', 10**999)

    def test_boolean_gates_are_strict(self):
        d = Deadman()
        d.update(False, True, 0, 0)
        self.assertFalse(d.update('false', True, .1, .1))
        self.assertFalse(d.update(True, True, .2, .2))
        self.assertEqual(hand_velocity(1, 1, enabled='true'), (0, 0))
        self.assertEqual(hand_velocity(True, 1, enabled=True), (0, 0))
        self.assertEqual(LandingController().update((0, 0, .1), contact=1).state, 'abort')
