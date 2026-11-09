import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import io
import unittest
from gesture_control.recording import record, replay


class RecordingTests(unittest.TestCase):
    def test_formats(self):
        events = [dict(time=1, mode='LOITER', battery=80, ack='hold=OK')]
        for fmt in ('csv', 'jsonl'):
            stream = io.StringIO()
            self.assertEqual(record(stream, events, fmt), 1)
            stream.seek(0)
            self.assertEqual(list(replay(stream, fmt)), events)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            record(io.StringIO(), [dict(secret='not allowed')])
        with self.assertRaises(ValueError):
            list(replay(io.StringIO('{"time":NaN}')))
