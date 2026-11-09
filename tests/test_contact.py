import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.contact import ContactConfirmation


class ContactTests(unittest.TestCase):
    def test_bounce_height_and_dwell(self):
        c = ContactConfirmation()
        self.assertFalse(c.update(True, .1, 0))
        self.assertFalse(c.update(False, .1, .2))
        self.assertFalse(c.update(True, 2, .3))
        self.assertFalse(c.update(True, .1, .4))
        self.assertTrue(c.update(True, .1, .7))
        self.assertFalse(c.update(True, float('nan'), .8))
