import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import io
import unittest
from gesture_control.dataset import record, evaluate


class DatasetTests(unittest.TestCase):
    def test_roundtrip_and_empty(self):
        stream = io.StringIO()
        record(stream, [('fist', [(0, 0)] * 21)])
        stream.seek(0)
        result = evaluate(stream)
        self.assertEqual(result['accuracy'], 1)
        self.assertEqual(result['confusion']['fist']['fist'], 1)
        empty = io.StringIO()
        record(empty, [])
        empty.seek(0)
        self.assertIsNone(evaluate(empty)['accuracy'])
        with self.assertRaises(ValueError):
            evaluate(io.StringIO('bad'))
