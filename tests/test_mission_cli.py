"""Offline CLI checks using in-memory streams; never launch a flight node."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

from gesture_control.mission_cli import evaluate, main, read_bounded
from gesture_control.mission_schema import MAX_BYTES, Mission, Waypoint


def source():
    return Mission((Waypoint('a', 0, 0, 1),), speed=1).to_json()


class MissionCLITests(unittest.TestCase):
    def test_evaluation_has_explicit_offline_flags(self):
        result = evaluate(source())
        self.assertEqual(result['schema'], 'offline_mission_report_v1')
        self.assertIs(result['summary']['flight_validated'], False)
        self.assertEqual(result['samples'][-1]['phase'], 'complete')

    def test_summary_only_omits_samples(self):
        result = evaluate(source(), summary_only=True)
        self.assertNotIn('samples', result)
        with self.assertRaises(ValueError):
            evaluate(source(), summary_only='yes')

    def test_bounded_reader(self):
        self.assertEqual(read_bounded(io.BytesIO(source().encode())), source())
        for stream in (io.BytesIO(b'x' * (MAX_BYTES + 1)), io.BytesIO(b'\xff'), io.StringIO('{}')):
            with self.subTest(stream=type(stream)), self.assertRaises(ValueError):
                read_bounded(stream)

    def test_reader_never_requests_unbounded_read(self):
        class Guard:
            size = None
            def read(self, size):
                if self.size is None:
                    self.size = size
                    return b'{}'
                return b''
        guard = Guard()
        self.assertEqual(read_bounded(guard), '{}')
        self.assertEqual(guard.size, MAX_BYTES + 1)

    def test_main_reads_explicit_path_as_binary(self):
        output = io.StringIO()
        with patch('builtins.open', return_value=io.BytesIO(source().encode())) as opened:
            with contextlib.redirect_stdout(output):
                status = main(['example.json', '--summary-only'])
        self.assertEqual(status, 0)
        opened.assert_called_once_with('example.json', 'rb')
        self.assertIs(json.loads(output.getvalue())['summary']['flight_validated'], False)

    def test_main_failure_does_not_echo_payload_or_path(self):
        errors = io.StringIO()
        with patch('builtins.open', side_effect=OSError('private details')):
            with contextlib.redirect_stderr(errors):
                status = main(['private_input.json'])
        self.assertEqual(status, 2)
        self.assertNotIn('private', errors.getvalue())
        self.assertEqual(json.loads(errors.getvalue())['error'], 'input_io_error')

    def test_main_invalid_plan_is_structured_failure(self):
        errors = io.StringIO()
        with patch('builtins.open', return_value=io.BytesIO(b'{"attack":"untrusted text"}')):
            with contextlib.redirect_stderr(errors):
                status = main(['input.json'])
        self.assertEqual(status, 2)
        self.assertNotIn('untrusted text', errors.getvalue())
        self.assertEqual(json.loads(errors.getvalue())['error'], 'invalid_offline_mission')

    def test_unknown_send_option_is_rejected(self):
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors), self.assertRaises(SystemExit) as result:
            main(['input.json', '--send'])
        self.assertEqual(result.exception.code, 2)

    def test_sampling_over_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(source(), interval=.001, max_samples=2)

    def test_short_reads_do_not_truncate_json(self):
        class Chunks:
            def __init__(self, data):
                self.data = data
            def read(self, size):
                result, self.data = self.data[:min(size, 3)], self.data[min(size, 3):]
                return result
        self.assertEqual(read_bounded(Chunks(source().encode())), source())

    def test_summary_only_still_validates_resource_configuration(self):
        for kwargs in ({'interval': True}, {'interval': 0}, {'max_samples': True},
                       {'max_samples': 0}, {'max_samples': 100001}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                evaluate(source(), summary_only=True, **kwargs)

    def test_checked_in_valid_examples_have_expected_durations(self):
        root = Path(__file__).resolve().parents[1] / 'docs/company/backend/examples'
        for name, duration, length in (('inspection_square.json', 50, 9),
                                       ('dwell_only.json', 2, 0)):
            with self.subTest(name=name):
                result = evaluate((root / name).read_text(encoding='utf-8'), summary_only=True)
                self.assertEqual(result['summary']['duration_s'], duration)
                self.assertEqual(result['summary']['distance_m'], length)

    def test_checked_in_boundary_fixture_is_rejected(self):
        root = Path(__file__).resolve().parents[1] / 'docs/company/backend/examples'
        with self.assertRaises(ValueError):
            evaluate((root / 'rejected_boundary.json').read_text(encoding='utf-8'))
