import copy
from pathlib import Path
import unittest
from drone_bringup.core_configuration import SCHEMA, parse_core_yaml, validate_core


class CoreYamlTests(unittest.TestCase):
    def setUp(self):
        self.text = (Path(__file__).resolve().parents[1] / 'config/core.yaml').read_text()
        self.data = parse_core_yaml(self.text)

    def test_repository_file(self):
        self.assertEqual(self.data['gesture_node']['ros__parameters']['camera_fps'], 30.)

    def test_comment_marker_in_quoted_path_is_preserved(self):
        data = parse_core_yaml(self.text.replace('pose_profile_path: ""',
                                                'pose_profile_path: "calibration#1.json" # comment'))
        self.assertEqual(data['gesture_node']['ros__parameters']['pose_profile_path'], 'calibration#1.json')

    def test_every_field_rejects_wrong_types_and_out_of_bounds(self):
        for node, fields in SCHEMA.items():
            for key, (_, low, high, _) in fields.items():
                for value in (True, None, '1', [], float('nan'), float('inf'), low-1, high+1):
                    data = copy.deepcopy(self.data)
                    data[node]['ros__parameters'][key] = value
                    with self.subTest(node=node, key=key, value=value):
                        with self.assertRaises(ValueError):
                            validate_core(data)

    def test_unsupported_yaml_and_duplicates(self):
        for text in (self.text + 'gesture_node:\n',
                     self.text.replace('    camera_index: 0', '    camera_index: 0\n    camera_index: 1'),
                     self.text.replace('camera_index: 0', 'camera_index: true'),
                     self.text.replace('camera_index: 0', 'camera_index: !!int 0'),
                     self.text.replace('camera_index: 0', 'camera_index: &camera 0'),
                     self.text.replace('    camera_index', '\tcamera_index'),
                     self.text.replace('camera_index', 'unknown_parameter'),
                     self.text.replace('hold_after_sec: 2.0', 'hold_after_sec: 6.0'),
                     ' ' * 16385):
            with self.assertRaises(ValueError):
                parse_core_yaml(text)
