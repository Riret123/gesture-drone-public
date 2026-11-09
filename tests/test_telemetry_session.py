from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.telemetry_session import TelemetrySession
from gesture_control.telemetry_contract import decode_telemetry


class TelemetrySessionTests(unittest.TestCase):
    def sample(self):
        return dict(schema=1, mock=True, age=0, mode='SIM', battery=70,
                    deadman=False, acks=[])

    def test_receive_clock_owned_and_stale_at_boundary(self):
        session = TelemetrySession('local_1', 1)
        self.assertEqual(session.receive('local_1', 0, self.sample(), 10).status, 'MOCK')
        self.assertEqual(session.view(10.999).status, 'MOCK')
        self.assertEqual(session.view(11).status, 'STALE')

    def test_duplicate_sequence_invalidates_instead_of_renewing(self):
        session = TelemetrySession('a', 1)
        session.receive('a', 2, self.sample(), 0)
        self.assertEqual(session.receive('a', 2, self.sample(), .9).status, 'INVALID')
        self.assertEqual(session.view(.9).status, 'OFFLINE')
        self.assertEqual(session.receive('a', 3, self.sample(), 1).status, 'MOCK')

    def test_malformed_packet_does_not_consume_sequence(self):
        session = TelemetrySession('a', 1)
        self.assertEqual(session.receive('a', 10, {}, 0).status, 'INVALID')
        self.assertEqual(session.receive('a', 1, self.sample(), 0).status, 'MOCK')

    def test_wrong_session_and_boolean_sequence(self):
        for name, sequence in [('b', 0), ('a', True), ('a', -1), ('a', 2**63)]:
            session = TelemetrySession('a', 1)
            self.assertEqual(session.receive(name, sequence, self.sample(), 0).status,
                             'INVALID')

    def test_clock_reversal_clears_previous_sample(self):
        session = TelemetrySession('a', 1)
        session.receive('a', 0, self.sample(), 2)
        with self.assertRaises(ValueError):
            session.view(1)
        self.assertEqual(session.view(2).status, 'OFFLINE')

    def test_payload_mutation_cannot_rewrite_snapshot(self):
        session = TelemetrySession('a', 1)
        sample = self.sample()
        session.receive('a', 0, sample, 0)
        sample['battery'] = 0
        sample['acks'].append('forged later')
        self.assertEqual(session.view(0).battery_percent, 70)
        self.assertEqual(session.view(0).acknowledgements, ())

    def test_source_age_is_not_reset_by_receive(self):
        session = TelemetrySession('a', 1)
        sample = self.sample()
        sample['age'] = .5
        session.receive('a', 0, sample, 0)
        self.assertEqual(session.view(.5).status, 'STALE')

    def test_new_session_requires_new_instance(self):
        session = TelemetrySession('a', 1)
        session.receive('a', 100, self.sample(), 0)
        self.assertEqual(session.receive('b', 0, self.sample(), 1).status, 'INVALID')
        replacement = TelemetrySession('b', 1)
        self.assertEqual(replacement.receive('b', 0, self.sample(), 1).status, 'MOCK')

    def test_identifiers_and_age_limits(self):
        for name in ['', 'a b', 'x'*65, 'русский', False]:
            with self.assertRaises(ValueError):
                TelemetrySession(name, 1)
        for age in [True, -1, 0, float('inf'), 10**10000]:
            with self.assertRaises(ValueError):
                TelemetrySession('a', age)

    def test_decoder_invalid_config_always_raises(self):
        for source in ['{}', b'\xff', 'x' * 20000]:
            with self.assertRaises(ValueError):
                decode_telemetry(source, 0, 0, False)
