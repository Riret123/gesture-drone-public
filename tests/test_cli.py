import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import contextlib
import io
import unittest
from gesture_control.cli_logic import parse_args
from gesture_control.dronectl import main


class CLITests(unittest.TestCase):
    def test_default_and_attestation(self):
        self.assertEqual(parse_args(['land']), ('land', False))
        self.assertEqual(parse_args(['hold', '--send', '--sitl-isolated']), ('hold', True))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(['takeoff', '--send'])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['land']), 0)
        self.assertIn('DRY RUN', output.getvalue())
