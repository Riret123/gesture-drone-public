import importlib.util
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from drone_bringup.deterministic_replay import Frame
from test_pose_features import pose


class CalibrationCaptureQualityTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'tools/calibrate_pose.py'
        spec = importlib.util.spec_from_file_location('calibration_quality_fixture', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.path = MagicMock()
        self.path.open.return_value.__enter__.return_value.read.return_value = 'inert fixture'

    def test_replayed_or_frozen_world_frames_cannot_calibrate(self):
        frozen = tuple(pose(True))
        frames = tuple(Frame(index / 10, (frozen,)) for index in range(10))
        with patch.object(self.module, 'read_landmark_csv', return_value=frames):
            with self.assertRaisesRegex(ValueError, 'distinct'):
                self.module.samples(self.path)

    def test_distinct_metric_poses_pass_capture_quality_gate(self):
        frames = tuple(Frame(index / 10, (tuple((x+index*.001, y, z)
                                                for x, y, z in pose(True)),))
                       for index in range(5))
        with patch.object(self.module, 'read_landmark_csv', return_value=frames):
            self.assertEqual(len(self.module.samples(self.path)), 5)

    def test_cli_refuses_source_tree_output_before_reading_samples(self):
        with patch.object(self.module, 'samples') as read, \
                patch.object(self.module, 'save_profile') as save, patch('builtins.print'):
            status = self.module.main(['--open', 'unused', '--fist', 'unused',
                                       '--coordinates', 'world', '--camera-id', 'camera-fixture',
                                       '--model-id', 'model-fixture', '--output',
                                       str(Path(__file__).resolve().parents[1] / 'forbidden-profile.json')])
        self.assertEqual(status, 2)
        read.assert_not_called()
        save.assert_not_called()
