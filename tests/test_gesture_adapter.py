"""Actual camera adapter under inert camera, inference and ROS doubles."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from gesture_control.safety import GestureSafety


def adapter():
    modules = {name: ModuleType(name) for name in (
        'cv2', 'mediapipe', 'rclpy', 'rclpy.node', 'std_msgs', 'std_msgs.msg')}
    class InertNode:
        def __init__(self, name):
            pass
        def declare_parameter(self, name, default):
            return SimpleNamespace(value=default)
        def create_publisher(self, *args):
            return Mock()
        def create_timer(self, *args):
            return Mock()
        def destroy_node(self):
            self.destroyed = True
    modules['rclpy.node'].Node = InertNode
    modules['std_msgs.msg'].String = lambda **kw: SimpleNamespace(**kw)
    path = Path(__file__).resolve().parents[1] / (
        'src/gesture_control/gesture_control/gesture_node.py')
    spec = importlib.util.spec_from_file_location('gesture_test_adapter', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class GestureAdapterTests(unittest.TestCase):
    def setUp(self):
        self.module = adapter()
        self.node = self.module.GestureNode.__new__(self.module.GestureNode)
        self.node._safety = GestureSafety(now=0)
        self.node._cap = Mock()
        self.node._hands = Mock()
        self.node._publisher = Mock()
        self.node._curl_ratio = 1.1
        self.node.get_logger = Mock(return_value=Mock())

    def test_camera_exception_still_advances_loss_policy(self):
        self.node._cap.read.side_effect = RuntimeError('camera disconnected')
        with patch.object(self.module.time, 'monotonic', return_value=5.0):
            self.node._on_timer()
        self.assertEqual(self.node._publisher.publish.call_args.args[0].data, 'land')

    def test_missing_frame_requests_hold_then_land(self):
        self.node._cap.read.return_value = (False, None)
        with patch.object(self.module.time, 'monotonic', side_effect=[2., 5.]):
            self.node._on_timer()
            self.node._on_timer()
        self.assertEqual([c.args[0].data for c in self.node._publisher.publish.call_args_list],
                         ['hold', 'land'])

    def test_inference_exception_does_not_renew_lease(self):
        self.node._cap.read.return_value = (True, object())
        self.module.cv2.flip = lambda frame, axis: frame
        self.module.cv2.COLOR_BGR2RGB = 1
        self.module.cv2.cvtColor = lambda *args: SimpleNamespace(
            flags=SimpleNamespace(writeable=True))
        self.node._hands.process.side_effect = RuntimeError('inference failure')
        with patch.object(self.module.time, 'monotonic', return_value=5.):
            self.node._on_timer()
        self.assertEqual(self.node._publisher.publish.call_args.args[0].data, 'land')

    def test_camera_cleanup_failure_still_closes_inference_and_ros(self):
        self.node._cap.release.side_effect = RuntimeError('release failure')
        with self.assertRaises(RuntimeError):
            self.node.destroy_node()
        self.node._hands.close.assert_called_once()
        self.assertTrue(self.node.destroyed)

    def test_inference_cleanup_failure_still_destroys_ros(self):
        self.node._hands.close.side_effect = RuntimeError('close failure')
        with self.assertRaises(RuntimeError):
            self.node.destroy_node()
        self.node._cap.release.assert_called_once()
        self.assertTrue(self.node.destroyed)

    def test_inference_startup_failure_releases_camera(self):
        camera = Mock()
        self.module.cv2.VideoCapture = Mock(return_value=camera)
        self.module.mp.solutions = SimpleNamespace(hands=SimpleNamespace(
            Hands=Mock(side_effect=RuntimeError('unsupported model API'))))
        with self.assertRaises(RuntimeError):
            self.module.GestureNode()
        camera.release.assert_called_once()

    def test_timer_startup_failure_releases_both_resources(self):
        camera, hands = Mock(), Mock()
        self.module.cv2.VideoCapture = Mock(return_value=camera)
        self.module.mp.solutions = SimpleNamespace(hands=SimpleNamespace(
            Hands=Mock(return_value=hands)))
        with patch.object(self.module.GestureNode, 'create_timer',
                          side_effect=RuntimeError('timer failure')):
            with self.assertRaises(RuntimeError):
                self.module.GestureNode()
        camera.release.assert_called_once()
        hands.close.assert_called_once()
