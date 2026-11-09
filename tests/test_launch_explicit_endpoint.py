import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


class LaunchEndpointTests(unittest.TestCase):
    def test_actual_launch_requires_fcu_and_keeps_other_routes_explicit(self):
        modules = {name: ModuleType(name) for name in (
            'launch', 'launch.actions', 'launch.launch_description_sources',
            'launch.substitutions', 'ament_index_python', 'ament_index_python.packages')}
        modules['launch'].LaunchDescription = lambda items: items
        modules['launch.actions'].DeclareLaunchArgument = lambda name, **kwargs: SimpleNamespace(
            kind='declare', name=name, options=kwargs)
        modules['launch.actions'].IncludeLaunchDescription = lambda source, **kwargs: SimpleNamespace(
            kind='include', source=source, options=kwargs)
        modules['launch.launch_description_sources'].AnyLaunchDescriptionSource = lambda path: path
        modules['launch.substitutions'].LaunchConfiguration = lambda name: 'ref:' + name
        modules['ament_index_python.packages'].get_package_share_directory = lambda name: '/installed/' + name
        path = Path(__file__).resolve().parents[1] / 'src/drone_bringup/launch/mavros_apm.launch.py'
        spec = importlib.util.spec_from_file_location('launch_endpoint_fixture', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(module)
            result = module.generate_launch_description()
        declarations = {item.name: item.options for item in result if item.kind == 'declare'}
        self.assertNotIn('default_value', declarations['fcu_url'])
        self.assertEqual(declarations['gcs_url']['default_value'], '')
        self.assertEqual(declarations['tgt_system']['default_value'], '1')
        self.assertEqual(declarations['tgt_component']['default_value'], '1')
        include = next(item for item in result if item.kind == 'include')
        self.assertTrue(include.source.endswith('apm.launch'))
        self.assertEqual(dict(include.options['launch_arguments']), {
            name: 'ref:' + name for name in ('fcu_url', 'gcs_url', 'tgt_system', 'tgt_component')})
