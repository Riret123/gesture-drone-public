import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.deadman import Deadman


class DeadmanTests(unittest.TestCase):
    def test_release_rearm_and_stale(self):
        d = Deadman()
        self.assertFalse(d.update(True, True, 0, 0))
        self.assertFalse(d.update(False, True, .05, .05))
        self.assertTrue(d.update(True, True, .1, .1))
        self.assertFalse(d.update(True, True, .1, .35))
        self.assertFalse(d.update(True, True, .4, .4))
        d.update(False, True, .5, .5)
        self.assertTrue(d.update(True, True, .6, .6))
        self.assertFalse(d.update(True, False, .7, .7))
