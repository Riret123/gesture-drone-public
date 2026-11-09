import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.sensor_evidence import EvidenceRequirement, EvidenceRecord
from gesture_control.sensor_evidence_session import EvidenceSession, SessionEvidence


class EvidenceSessionTests(unittest.TestCase):
    def setUp(self):
        self.req = EvidenceRequirement('camera', 'rig', 'v1', 10, ('measurement',))
        self.record = EvidenceRecord('camera', 'rig', 'v1', 'measurement', 1, 'audit-a', True)
        self.session = EvidenceSession('boot-a', [self.req])

    def test_s14_cross_reboot_monotonic_evidence_rejects(self):
        report = self.session.review([SessionEvidence('boot-b', self.record)], 2)
        self.assertEqual(report.status, 'INCOMPLETE')
        self.assertIn(('<session>', 'wrong_session'), report.findings)
        self.assertIn(('camera', 'missing'), report.findings)

    def test_matching_session_still_requires_record_policy(self):
        report = self.session.review([SessionEvidence('boot-a', self.record)], 2)
        self.assertEqual(report.status, 'METADATA_COMPLETE')
        report = self.session.review([SessionEvidence('boot-a', self.record)], 12)
        self.assertIn(('camera', 'expired'), report.findings)

    def test_input_policy_list_mutation_cannot_remove_requirements(self):
        requirements = [self.req]
        session = EvidenceSession('a', requirements)
        requirements.clear()
        self.assertIn(('camera', 'missing'), session.review([], 2).findings)

    def test_invalid_envelope_cannot_hide_missing_evidence(self):
        report = self.session.review([{}], 2)
        self.assertIn(('<session>', 'invalid_envelope'), report.findings)
        self.assertIn(('camera', 'missing'), report.findings)

    def test_invalid_constructor_or_clock_rejects(self):
        for session in ('', ' a', None, True):
            with self.assertRaises(ValueError):
                EvidenceSession(session, [self.req])
        with self.assertRaises(ValueError):
            EvidenceSession('a', [])
        with self.assertRaises(ValueError):
            self.session.review([], True)

    def test_s19_rewind_cannot_freshen_expired_evidence(self):
        envelope = SessionEvidence('boot-a', self.record)
        self.assertIn(('camera', 'expired'), self.session.review([envelope], 12).findings)
        report = self.session.review([envelope], 2)
        self.assertEqual(report.status, 'INCOMPLETE')
        self.assertIn(('<session>', 'clock_reversed'), report.findings)
