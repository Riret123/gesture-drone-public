import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.sensor_evidence import EvidenceRequirement, EvidenceRecord, review_evidence


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.req = EvidenceRequirement('calibration', 'camera-down', 'v1', 10., ('measurement',))
        self.record = EvidenceRecord('calibration', 'camera-down', 'v1', 'measurement', 1., 'audit-001', True)

    def review(self, *records, now=2.):
        return review_evidence([self.req], list(records), now)

    def test_metadata_complete_does_not_say_ready_or_safe(self):
        result = self.review(self.record)
        self.assertEqual(result.status, 'METADATA_COMPLETE')
        self.assertEqual(result.findings, ())

    def test_s05_human_checkbox_cannot_substitute_for_measurement(self):
        result = self.review(replace(self.record, origin='human_attestation'))
        self.assertIn(('calibration', 'unaccepted_origin'), result.findings)

    def test_missing_and_extra_keys(self):
        self.assertIn(('calibration', 'missing'), self.review().findings)
        result = self.review(self.record, replace(self.record, key='other'))
        self.assertIn(('other', 'unexpected_record'), result.findings)

    def test_wrong_scope_and_revision(self):
        result = self.review(replace(self.record, scope='camera-front', revision='v0'))
        self.assertIn(('calibration', 'wrong_scope'), result.findings)
        self.assertIn(('calibration', 'wrong_revision'), result.findings)

    def test_expired_future_and_invalid_times(self):
        self.assertEqual(self.review(self.record, now=11.).status, 'METADATA_COMPLETE')
        self.assertIn(('calibration', 'expired'), self.review(self.record, now=11.001).findings)
        for value in (3., True, -1., float('nan'), float('inf'), 10**1000):
            self.assertIn(('calibration', 'invalid_time'),
                          self.review(replace(self.record, observed_s=value)).findings)

    def test_truthy_result_does_not_pass(self):
        for value in (1, 'yes', None):
            self.assertIn(('calibration', 'invalid_result'),
                          self.review(replace(self.record, passed=value)).findings)
        self.assertIn(('calibration', 'failed'),
                      self.review(replace(self.record, passed=False)).findings)

    def test_duplicate_invalid_and_missing_reference(self):
        self.assertIn(('calibration', 'duplicate_record'),
                      self.review(self.record, self.record).findings)
        self.assertIn(('<record>', 'invalid_record'), self.review({}).findings)
        self.assertIn(('calibration', 'missing_reference'),
                      self.review(replace(self.record, reference=' ')).findings)

    def test_empty_requirements_and_invalid_policy_cannot_pass_vacuously(self):
        for requirements in ([], None, [self.req, self.req]):
            with self.assertRaises(ValueError):
                review_evidence(requirements, [], 1.)
        for origins in ((), ('unknown',), ['measurement'], ('measurement', 'measurement')):
            with self.assertRaises(ValueError):
                EvidenceRequirement('key', 'scope', 'v1', 1., origins)
        with self.assertRaises(ValueError):
            review_evidence([self.req], [], True)
