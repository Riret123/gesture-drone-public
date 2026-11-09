import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
import contextlib
import io
import json
import unittest
from unittest.mock import mock_open, patch
from gesture_control.dataset_cli import main, convert
from gesture_control.dataset import evaluate


class DatasetCLITests(unittest.TestCase):
    def test_conversion(self):
        sample = json.dumps(dict(label='fist', points=[[0, 0]] * 21))
        output = io.StringIO()
        self.assertEqual(convert(io.StringIO(sample), output), 1)
        output.seek(0)
        self.assertEqual(evaluate(output)['total'], 1)
        with self.assertRaises(ValueError):
            convert(io.StringIO('{}'), io.StringIO())

    def test_cli_exclusive_open_and_validation_before_write(self):
        sample = json.dumps(dict(label='fist', points=[[0, 0]] * 21))
        opener = mock_open(read_data=sample)
        with patch('builtins.open', opener), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['input.jsonl', 'output.csv']), 0)
        self.assertEqual(opener.call_args_list[1].args, ('output.csv', 'x'))
        invalid = mock_open(read_data='{}')
        with patch('builtins.open', invalid), self.assertRaises(ValueError):
            main(['input.jsonl', 'output.csv'])
        self.assertEqual(invalid.call_count, 1)
