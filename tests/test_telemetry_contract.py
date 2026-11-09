from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.telemetry_contract import normalize_telemetry


class TelemetryContractTests(unittest.TestCase):
    def sample(self):
        return dict(schema=1, mock=True, age=0., mode='SIMULATION', battery=50.,
                    deadman=False, acks=['accepted is not completed'])

    def test_mock_is_explicit(self):
        view = normalize_telemetry(self.sample(), 1., 1., 2.)
        self.assertEqual(view.status, 'MOCK')
        self.assertFalse(view.deadman)

    def test_source_and_transport_age_add(self):
        sample = self.sample()
        sample['age'] = 1.
        view = normalize_telemetry(sample, 1., 2., 2.)
        self.assertEqual(view.status, 'STALE')
        self.assertIsNone(view.battery_percent)

    def test_strict_fields_and_boolean_numbers(self):
        for field, value in [('schema', True), ('age', True), ('battery', False),
                             ('deadman', 1), ('mock', 'false'), ('mode', ''),
                             ('mode', 'a\ncommand'), ('acks', ['x' * 257])]:
            with self.subTest(field=field, value=value):
                sample = self.sample()
                sample[field] = value
                self.assertEqual(normalize_telemetry(sample, 0, 0, 1).status, 'INVALID')

    def test_unknown_and_missing_fields(self):
        sample = self.sample()
        sample['command'] = 'anything'
        self.assertEqual(normalize_telemetry(sample, 0, 0, 1).status, 'INVALID')
        del sample['command']
        del sample['schema']
        self.assertEqual(normalize_telemetry(sample, 0, 0, 1).status, 'INVALID')

    def test_clock_reversal_and_nonfinite(self):
        for receive, now in [(2, 1), (0, float('nan')), (False, 0)]:
            self.assertEqual(normalize_telemetry(self.sample(), receive, now, 1).status,
                             'INVALID')

    def test_history_snapshot_does_not_alias(self):
        sample = self.sample()
        view = normalize_telemetry(sample, 0, 0, 1)
        sample['acks'].append('later')
        self.assertEqual(len(view.acknowledgements), 1)

    def test_payload_bounds(self):
        for key, value in [('battery', float('inf')), ('age', -1),
                           ('acks', ['x'] * 31), ('mode', 'x' * 65)]:
            sample = self.sample()
            sample[key] = value
            self.assertEqual(normalize_telemetry(sample, 0, 0, 1).status, 'INVALID')

    def test_invalid_freshness_configuration(self):
        for limit in [0, -1, True, '1', float('nan')]:
            with self.assertRaises(ValueError):
                normalize_telemetry(self.sample(), 0, 0, limit)
