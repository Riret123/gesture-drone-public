import importlib.util
from pathlib import Path
import unittest


class PortableManifestTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_excludes_forbidden_roots(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('portable_manifest_fixture',
                                                     root / 'tools/verify_portable.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        before = module.source_manifest(root)
        self.assertEqual(before, module.source_manifest(root))
        self.assertIn('config/core.yaml', before)
        self.assertIn('test_flight_cmd_bridge.py', before)
        self.assertIn('src/drone_bringup/drone_bringup/flight_logic.py', before)
        self.assertTrue(all(not key.startswith(('network/', 'docs/', '.git/')) for key in before))
        self.assertTrue(all(len(value) == 64 for value in before.values()))
