import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from gesture_control.gesture_classifier import classify_gesture


class PreviewAdapterTests(unittest.TestCase):
    def setUp(self):
        self.cv = Mock()
        self.mp = Mock()
        path = Path(__file__).resolve().parents[1] / 'gesture_test.py'
        spec = importlib.util.spec_from_file_location('preview_test', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'cv2': self.cv, 'mediapipe': self.mp}):
            spec.loader.exec_module(self.module)

    def test_preview_uses_live_classifier_for_invalid_geometry(self):
        points = [SimpleNamespace(x=float('nan'), y=0.) for _ in range(21)]
        self.assertEqual(self.module.classify_gesture(points), classify_gesture(points))

    def test_model_startup_failure_cleans_camera_and_windows(self):
        self.mp.solutions.hands.Hands.side_effect = RuntimeError('model failure')
        with self.assertRaises(RuntimeError):
            self.module.main()
        self.cv.VideoCapture.return_value.release.assert_called_once()
        self.cv.destroyAllWindows.assert_called_once()

    def test_camera_open_failure_releases_capture(self):
        self.cv.VideoCapture.return_value.isOpened.return_value = False
        self.module.main()
        self.cv.VideoCapture.return_value.release.assert_called_once()
