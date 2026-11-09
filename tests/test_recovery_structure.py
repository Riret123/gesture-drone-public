"""Detect interrupted source merges that ordinary imports can silently hide."""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RecoveryStructureTests(unittest.TestCase):
    def test_source_scopes_have_no_shadowed_definitions(self):
        paths = sorted((ROOT / 'src').rglob('*.py'))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
                for scope in ast.walk(tree):
                    if not isinstance(scope, (ast.Module, ast.ClassDef,
                                              ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    names = [node.name for node in scope.body if isinstance(
                        node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
                    self.assertEqual(len(names), len(set(names)),
                                     f'duplicate definitions in {getattr(scope, "name", "module")}')

    def test_no_adapter_methods_nested_inside_entrypoint(self):
        for relative in ('drone_bringup/drone_bringup/flight_cmd_bridge.py',
                         'gesture_control/gesture_control/gesture_node.py'):
            tree = ast.parse((ROOT / 'src' / relative).read_text(encoding='utf-8-sig'))
            mains = [node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == 'main']
            self.assertEqual(len(mains), 1, relative)
            nested = [node.name for node in ast.walk(mains[0])
                      if isinstance(node, ast.FunctionDef) and node is not mains[0]]
            self.assertEqual(nested, [], relative)
