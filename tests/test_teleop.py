import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.teleop_logic import command_for_key


class TeleopTests(unittest.TestCase):
    def test_mapping(self):
        for key, expected in [('t', 'open_palm'), ('T', 'open_palm'),
                              ('l', 'land'), ('h', 'hold'), (' ', 'emergency')]:
            self.assertEqual(command_for_key(key), expected)

    def test_unknown(self):
        for key in ('', 'q', '\n', '\x03', 'w', 'takeoff'):
            self.assertIsNone(command_for_key(key))
