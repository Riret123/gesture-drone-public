from pathlib import Path
import sys
import json
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.telemetry_contract import normalize_telemetry

FIXTURES = Path(__file__).parent / 'fixtures/telemetry_contract.json'


class TelemetryParityFixturesTests(unittest.TestCase):
    def test_shared_semantic_vectors(self):
        cases = json.loads(FIXTURES.read_text(encoding='utf-8'))
        self.assertEqual(len({c['name'] for c in cases}), len(cases))
        for case in cases:
            with self.subTest(name=case['name']):
                view = normalize_telemetry(case['payload'], 0, case['elapsed'], 2)
                self.assertEqual(view.status, case['python_status'])

    def test_corpus_has_required_adversarial_categories(self):
        names = {case['name'] for case in json.loads(FIXTURES.read_text(encoding='utf-8'))}
        self.assertTrue({'schema_bool','bool_battery','stale_at_limit','mode_direction',
                         'mode_surrogate','history_too_many','unknown_field'} <= names)
