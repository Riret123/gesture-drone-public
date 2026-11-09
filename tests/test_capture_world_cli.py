import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class CaptureWorldCliTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'tools/capture_world.py'
        spec = importlib.util.spec_from_file_location('capture_world_cli_fixture', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_default_plan_does_not_import_camera_libraries(self):
        destination = Mock()
        with patch.object(self.module, 'output_path', return_value=destination), \
                patch('builtins.print'):
            self.assertEqual(self.module.main(['--label', 'fist', '--output', 'unused']), 0)
        destination.open.assert_not_called()

    def test_inside_checkout_output_rejects_before_capture(self):
        path = Path(__file__).resolve().parents[1] / 'forbidden-recording.csv'
        with self.assertRaises(ValueError):
            self.module.output_path(str(path))
        self.assertFalse(path.exists())

    def test_inference_startup_failure_releases_camera_and_writes_nothing(self):
        cap, model, destination = Mock(), Mock(), Mock()
        cap.get.side_effect = lambda key: {3: 640., 4: 480., 5: 30.}[key]
        model.side_effect = RuntimeError('synthetic model startup failure')
        cv = SimpleNamespace(VideoCapture=Mock(return_value=cap), CAP_PROP_FRAME_WIDTH=3,
                             CAP_PROP_FRAME_HEIGHT=4, CAP_PROP_FPS=5)
        mp = SimpleNamespace(__version__='fixture', solutions=SimpleNamespace(
            hands=SimpleNamespace(Hands=model)))
        with patch.dict(sys.modules, {'cv2': cv, 'mediapipe': mp}), \
                patch.object(self.module, 'output_path', return_value=destination), \
                patch('builtins.print'):
            self.assertEqual(self.module.main(['--capture', '--label', 'fist', '--output', 'unused']), 2)
        cap.release.assert_called_once()
        destination.open.assert_not_called()

    def test_cleanup_failure_cannot_print_success_or_write_dataset(self):
        cap, model, destination = Mock(), Mock(), Mock()
        cap.get.side_effect = lambda key: {3: 640., 4: 480., 5: 30.}[key]
        cap.release.side_effect = RuntimeError('synthetic cleanup failure')
        cv = SimpleNamespace(VideoCapture=Mock(return_value=cap), CAP_PROP_FRAME_WIDTH=3,
                             CAP_PROP_FRAME_HEIGHT=4, CAP_PROP_FPS=5)
        mp = SimpleNamespace(__version__='fixture', solutions=SimpleNamespace(
            hands=SimpleNamespace(Hands=Mock(return_value=model))))
        with patch.dict(sys.modules, {'cv2': cv, 'mediapipe': mp}), \
                patch.object(self.module, 'output_path', return_value=destination), \
                patch.object(self.module, 'collect_world', return_value=((), {'complete': True})), \
                patch('builtins.print'):
            self.assertEqual(self.module.main(['--capture', '--label', 'fist', '--output', 'unused']), 2)
        model.close.assert_called_once()
        destination.open.assert_not_called()
