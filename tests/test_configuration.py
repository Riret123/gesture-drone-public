import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.configuration import OfflineConfig


class ConfigurationTests(unittest.TestCase):
    def test_strict_schema(self):
        self.assertEqual(OfflineConfig.from_dict({}).rover_timeout, .5)
        for bad in ({'version': True}, {'version': 2}, {'password': 'redacted'},
                    {'rover_timeout': 20}, {'wheel_track': float('nan')},
                    {'wheel_speed': True}, {'wheel_speed': .5}):
            with self.assertRaises(ValueError):
                OfflineConfig.from_dict(bad)
