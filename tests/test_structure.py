import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import ast
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WRAPPERS = {'gesture_node.py', 'keyboard_teleop.py', 'dronectl.py', 'flight_cmd_bridge.py'}


class StructureTests(unittest.TestCase):
    def test_logic_import_boundary_and_syntax(self):
        for base in ('src/gesture_control/gesture_control', 'src/drone_bringup/drone_bringup'):
            for path in (ROOT / base).glob('*.py'):
                source = path.read_text(encoding='utf-8-sig')
                tree = ast.parse(source)
                if path.name in WRAPPERS:
                    continue
                for node in ast.walk(tree):
                    names = [a.name for a in node.names] if isinstance(node, ast.Import) else []
                    if isinstance(node, ast.ImportFrom):
                        names.append(node.module or '')
                    self.assertFalse(any(n.split('.')[0] in {'rclpy', 'mediapipe'} for n in names), path)

    def test_entry_points_and_manifests(self):
        for package in ('gesture_control', 'drone_bringup'):
            base = ROOT / 'src' / package
            self.assertEqual(ET.parse(base / 'package.xml').findtext('name'), package)
            self.assertTrue((base / 'resource' / package).is_file())
        setup = (ROOT / 'src/gesture_control/setup.py').read_text(encoding='utf-8')
        self.assertIn('dronectl = gesture_control.dronectl:main', setup)
