"""Headless camera adapter for the pure gesture safety policy."""
import time
import math
import uuid
import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from gesture_control.gesture_classifier import classify_gesture
from gesture_control.safety import GestureSafety
from gesture_control.camera_settings import CameraSettings
from gesture_control.frame_classifier import classify_frame
from gesture_control.pose_profile_io import load_profile


class GestureNode(Node):
    def __init__(self):
        super().__init__('gesture_node')
        frames = self.declare_parameter('debounce_frames', 5).value
        hold = self.declare_parameter('hold_after_sec', 2.0).value
        land = self.declare_parameter('land_after_sec', 5.0).value
        self._safety = GestureSafety(frames, hold, land, time.monotonic())
        if (frames > 120 or not .1 <= hold <= 10 or not .2 <= land <= 30):
            raise ValueError('require frames <=120, hold [0.1,10], land [0.2,30]')
        self._curl_ratio = self.declare_parameter('curl_ratio', 1.1).value
        classify_gesture([], self._curl_ratio)  # Validate before opening hardware.
        camera = self.declare_parameter('camera_index', 0).value
        detection = self.declare_parameter('detection_confidence', 0.6).value
        tracking = self.declare_parameter('tracking_confidence', 0.5).value
        settings = CameraSettings(
            self.declare_parameter('camera_width', 640).value,
            self.declare_parameter('camera_height', 480).value,
            self.declare_parameter('camera_fps', 30.0).value,
            self.declare_parameter('model_complexity', 0).value)
        profile_path = self.declare_parameter('pose_profile_path', '').value
        if (not isinstance(profile_path, str) or len(profile_path) > 1024
                or any(c in profile_path for c in '\x00\r\n')):
            raise ValueError('pose_profile_path must be a bounded local path')
        self._pose_profile = None
        if profile_path:
            version = getattr(mp, '__version__', 'unknown')
            if version == 'unknown':
                raise ValueError('calibration requires identified MediaPipe version')
            self._pose_profile = load_profile(
                profile_path, camera_id=(f'camera-{camera}-{settings.width}x{settings.height}'
                                         f'-{settings.fps:g}fps-mirror1'),
                model_id=f'mediapipe:{version}:hands-world:model{settings.model_complexity}')
        self._frame_budget_ms = self.declare_parameter('frame_budget_ms', 200.0).value
        if (isinstance(self._frame_budget_ms, bool)
                or not isinstance(self._frame_budget_ms, (int, float))
                or not math.isfinite(self._frame_budget_ms)
                or not 20 <= self._frame_budget_ms <= 500):
            raise ValueError('frame_budget_ms must be in [20,500]')
        if isinstance(camera, bool) or not isinstance(camera, int) or not 0 <= camera <= 32:
            raise ValueError('camera_index must be an integer in [0,32]')
        for confidence in (detection, tracking):
            if (isinstance(confidence, bool) or not isinstance(confidence, (int, float))
                    or not math.isfinite(confidence) or not 0 < confidence <= 1):
                raise ValueError('confidence must be in (0, 1]')
        self._publisher = self.create_publisher(String, '/flight_cmd', 10)
        self._heartbeat_session = uuid.uuid4().hex
        self._heartbeat_seq = 0
        self._heartbeat_pub = self.create_publisher(String, '/gesture_heartbeat', 1)
        self._cap = self._hands = None
        try:
            self._cap = cv2.VideoCapture(camera)
            self._cap.set(getattr(cv2, 'CAP_PROP_FRAME_WIDTH', 3), settings.width)
            self._cap.set(getattr(cv2, 'CAP_PROP_FRAME_HEIGHT', 4), settings.height)
            self._cap.set(getattr(cv2, 'CAP_PROP_FPS', 5), settings.fps)
            if self._pose_profile is not None and not settings.matches(
                    self._cap.get(getattr(cv2, 'CAP_PROP_FRAME_WIDTH', 3)),
                    self._cap.get(getattr(cv2, 'CAP_PROP_FRAME_HEIGHT', 4)),
                    self._cap.get(getattr(cv2, 'CAP_PROP_FPS', 5))):
                raise ValueError('negotiated camera settings do not match calibration identity')
            self._hands = mp.solutions.hands.Hands(
                model_complexity=settings.model_complexity, min_detection_confidence=detection,
                min_tracking_confidence=tracking, max_num_hands=2)
            self._timer = self.create_timer(1 / settings.fps, self._on_timer)
        except Exception:
            try:
                self.destroy_node()
            except Exception:
                pass  # Preserve the startup exception after best-effort cleanup.
            raise

    def _on_timer(self):
        gestures = []
        started = time.perf_counter()
        try:
            ok, frame = self._cap.read()
            if ok:
                rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                rgb.flags.writeable = False
                results = self._hands.process(rgb)
                profile = getattr(self, '_pose_profile', None)
                worlds = None
                if profile is not None:
                    worlds = [[(p.x, p.y, p.z) for p in hand.landmark]
                              for hand in results.multi_hand_world_landmarks or []]
                gestures = classify_frame(
                    [hand.landmark for hand in results.multi_hand_landmarks or []],
                    self._curl_ratio, world_hands=worlds, profile=profile)
                elapsed_ms = (time.perf_counter() - started) * 1000
                if (not math.isfinite(elapsed_ms) or elapsed_ms < 0
                        or elapsed_ms > getattr(self, '_frame_budget_ms', 200.)):
                    gestures = []
        except Exception:
            # A returned camera/inference failure is missing input, not a lease
            # renewal. A blocked native call still needs an external watchdog.
            gestures = []
            self.get_logger().error('Camera/inference failure; input lease not renewed',
                                    throttle_duration_sec=5.0)
        command = self._safety.update(gestures, time.monotonic())
        if command:
            self._publisher.publish(String(data=command))
        heartbeat = getattr(self, '_heartbeat_pub', None)
        if heartbeat is not None:
            self._heartbeat_seq = getattr(self, '_heartbeat_seq', 0) + 1
            session = getattr(self, '_heartbeat_session', '0' * 32)
            heartbeat.publish(String(data=f'v1:{session}:{self._heartbeat_seq}:{time.monotonic():.9f}'))

    def destroy_node(self):
        try:
            if self._cap is not None:
                self._cap.release()
        finally:
            try:
                if self._hands is not None:
                    self._hands.close()
            finally:
                super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = GestureNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if node is not None:
                node.destroy_node()
        finally:
            rclpy.shutdown()
