from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.mock_server import telemetry
from gesture_control.telemetry_contract import normalize_telemetry

ROOT = Path(__file__).resolve().parents[1]


class TelemetryAssetTests(unittest.TestCase):
    def test_mock_provider_conforms_to_normalizer(self):
        self.assertEqual(normalize_telemetry(telemetry(), 0, 0, 2).status, 'MOCK')

    def test_both_pages_use_shared_adapter(self):
        for name in ['dashboard/index.html', 'quest/index.html']:
            source = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn('src="/telemetry_ui.js"', source)
            self.assertNotIn('async function pollTelemetry', source)

    def test_shared_adapter_has_readonly_text_boundary(self):
        source = (ROOT / 'dashboard/telemetry.js').read_text(encoding='utf-8')
        self.assertNotIn('innerHTML', source)
        self.assertNotIn('WebSocket', source)
        self.assertNotIn('POST', source)
        self.assertIn('textContent', source)
        self.assertIn('readBounded', source)

    def test_mock_route_is_fixed_not_filesystem_passthrough(self):
        source = (ROOT / 'src/gesture_control/gesture_control/mock_server.py').read_text(encoding='utf-8')
        self.assertIn("self.path == '/telemetry_ui.js'", source)
        self.assertIn("root / 'dashboard/telemetry.js'", source)
