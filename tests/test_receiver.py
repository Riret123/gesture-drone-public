import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.receiver import RoverSession
from gesture_control.protocol import encode


class ReceiverTests(unittest.TestCase):
    def test_replay_does_not_renew_watchdog(self):
        r = RoverSession()
        packet = encode(10, 'follow', .1)
        self.assertTrue(r.accept(packet, 0))
        self.assertFalse(r.accept(packet, .4))
        self.assertFalse(r.accept(b'corrupt', .45))
        self.assertEqual(r.poll(.5), (0, 0))
        self.assertFalse(r.accept(encode(9, 'hold'), .6))
        r.reset(.6)
        self.assertTrue(r.accept(encode(1, 'hold', .2), .6))
        self.assertEqual(r.poll(.6), (0, 0))

    def test_reset_only_stopped(self):
        r = RoverSession()
        r.accept(encode(1, 'follow', .1), 0)
        with self.assertRaises(ValueError):
            r.reset(0)
