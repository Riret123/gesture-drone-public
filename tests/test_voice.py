import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.voice import parse


class VoiceTests(unittest.TestCase):
    def test_bilingual_and_negation(self):
        self.assertEqual(parse('  TAKE   OFF '), 'open_palm')
        self.assertEqual(parse('ВЗЛЁТ'), 'open_palm')
        self.assertEqual(parse('аварийная посадка'), 'emergency')
        for text in ('do not land', 'не взлет', 'land then takeoff', 'island', ''):
            self.assertIsNone(parse(text))
