"""No camera or socket opens: test real main with inert dependencies."""
import importlib.util
from pathlib import Path
import sys
import threading
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


class VideoLifecycleTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'video_stream_server.py'
        spec = importlib.util.spec_from_file_location('video_test_module', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'cv2': ModuleType('cv2')}):
            spec.loader.exec_module(self.module)

    def test_loopback_host_argument(self):
        server = Mock()
        server.serve_forever.side_effect = KeyboardInterrupt
        with patch.object(self.module, 'SharedCamera') as camera, \
                patch.object(self.module, 'ThreadingHTTPServer', return_value=server) as factory, \
                patch.object(sys, 'argv', ['video', '--host', '127.0.0.1']):
            self.module.main()
        self.assertEqual(factory.call_args.args[0], ('127.0.0.1', 8080))
        camera.return_value.stop.assert_called_once()
        server.server_close.assert_called_once()

    def test_bind_failure_releases_camera(self):
        with patch.object(self.module, 'SharedCamera') as camera, \
                patch.object(self.module, 'ThreadingHTTPServer', side_effect=OSError('busy')), \
                patch.object(sys, 'argv', ['video']):
            with self.assertRaises(OSError):
                self.module.main()
        camera.return_value.stop.assert_called_once()

    def test_invalid_fps_rejected_before_camera(self):
        with patch.object(self.module, 'SharedCamera') as camera, \
                patch.object(sys, 'argv', ['video', '--fps', '0']):
            with self.assertRaises(SystemExit):
                self.module.main()
        camera.assert_not_called()

    def test_stale_frame_is_not_republished_as_live(self):
        camera = self.module.SharedCamera.__new__(self.module.SharedCamera)
        camera._lock = threading.Lock()
        camera._frame = Mock()
        camera._frame_time = 10.
        camera._max_age = 2.
        with patch.object(self.module.time, 'monotonic', return_value=12.):
            self.assertIsNone(camera.get_frame())
        camera._frame.copy.assert_not_called()

    def test_frame_clock_reversal_rejects(self):
        camera = self.module.SharedCamera.__new__(self.module.SharedCamera)
        camera._lock = threading.Lock()
        camera._frame = Mock()
        camera._frame_time = 10.
        camera._max_age = 2.
        with patch.object(self.module.time, 'monotonic', return_value=9.):
            self.assertIsNone(camera.get_frame())
