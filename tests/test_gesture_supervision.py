from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import test_gesture_adapter as gesture_fixture
import test_bridge_link_guard as bridge_fixture
from test_core_chain import hand
from test_pose_features import pose
from gesture_control.pose_features import PoseProfile
from gesture_control.safety import GestureSafety


class FrameBudgetTests(unittest.TestCase):
    def setUp(self):
        gesture_fixture.GestureAdapterTests.setUp(self)

    def setup_frame(self):
        self.node._cap.read.return_value = (True, object())
        self.node._heartbeat_pub = Mock()
        self.module.cv2.flip = lambda frame, axis: frame
        self.module.cv2.COLOR_BGR2RGB = 1
        self.module.cv2.cvtColor = lambda *args: SimpleNamespace(flags=SimpleNamespace(writeable=True))
        self.node._hands.process.return_value = SimpleNamespace(
            multi_hand_landmarks=[SimpleNamespace(landmark=hand(True))])
        self.node._safety = GestureSafety(frames=1, now=0.)

    def test_slow_frame_cannot_renew_input_lease_but_reports_process_alive(self):
        self.setup_frame()
        with patch.object(self.module.time, 'perf_counter', side_effect=[0., .201]), \
                patch.object(self.module.time, 'monotonic', return_value=5.):
            self.node._on_timer()
        self.assertEqual(self.node._publisher.publish.call_args.args[0].data, 'land')
        self.node._heartbeat_pub.publish.assert_called_once()

    def test_slow_two_fists_cannot_suppress_input_loss_land_forever(self):
        self.setup_frame()
        self.node._hands.process.return_value = SimpleNamespace(multi_hand_landmarks=[
            SimpleNamespace(landmark=hand(False)), SimpleNamespace(landmark=hand(False))])
        land_time = None
        for tick in range(1, 31):
            now = tick * .3
            with patch.object(self.module.time, 'monotonic', return_value=now), \
                    patch.object(self.module.time, 'perf_counter', side_effect=[0., .3]):
                self.node._on_timer()
            if self.node._publisher.publish.called:
                if self.node._publisher.publish.call_args.args[0].data == 'land' and land_time is None:
                    land_time = now
        self.assertEqual([call.args[0].data for call in self.node._publisher.publish.call_args_list],
                         ['hold', 'land'])
        self.assertIsNotNone(land_time)
        self.assertLessEqual(land_time, 5.4)

    def test_world_profile_uses_world_outputs_and_missing_world_abstains(self):
        self.setup_frame()
        self.node._pose_profile = PoseProfile()
        self.node._hands.process.return_value.multi_hand_world_landmarks = [
            SimpleNamespace(landmark=[SimpleNamespace(x=x, y=y, z=z) for x, y, z in pose(False)])]
        with patch.object(self.module.time, 'monotonic', return_value=.1):
            self.node._on_timer()
        self.assertEqual(self.node._publisher.publish.call_args.args[0].data, 'fist')
        self.node._hands.process.return_value.multi_hand_world_landmarks = []
        with patch.object(self.module.time, 'monotonic', return_value=5.1):
            self.node._on_timer()
        self.assertEqual(self.node._publisher.publish.call_args.args[0].data, 'land')

    def test_invalid_profile_rejects_before_camera_acquisition(self):
        self.module.mp.__version__ = 'fixture'
        self.module.cv2.VideoCapture = Mock()
        def parameter(node, name, default):
            return SimpleNamespace(value='missing-profile-for-test.json'
                                   if name == 'pose_profile_path' else default)
        with patch.object(self.module.GestureNode, 'declare_parameter', new=parameter):
            with self.assertRaises(OSError):
                self.module.GestureNode()
        self.module.cv2.VideoCapture.assert_not_called()

    def test_negotiated_camera_mismatch_releases_camera_without_starting_model(self):
        self.module.mp.__version__ = 'fixture'
        camera = Mock()
        camera.get.side_effect = lambda key: {3: 320., 4: 240., 5: 15.}[key]
        self.module.cv2.VideoCapture = Mock(return_value=camera)
        model = Mock()
        self.module.mp.solutions = SimpleNamespace(hands=SimpleNamespace(Hands=model))
        def parameter(node, name, default):
            return SimpleNamespace(value='fixture-profile.json' if name == 'pose_profile_path' else default)
        with patch.object(self.module, 'load_profile', return_value=PoseProfile()), \
                patch.object(self.module.GestureNode, 'declare_parameter', new=parameter):
            with self.assertRaisesRegex(ValueError, 'negotiated'):
                self.module.GestureNode()
        camera.release.assert_called_once()
        model.assert_not_called()


class GestureHeartbeatTests(unittest.TestCase):
    def setUp(self):
        bridge_fixture.BridgeLinkGuardTests.setUp(self)

    def test_stall_boundary_and_no_automatic_recovery(self):
        self.bridge._gesture_timeout = 3.
        self.bridge._on_flight_cmd = Mock()
        with patch.object(self.module.time, 'monotonic', return_value=1.):
            self.bridge._on_gesture_heartbeat(SimpleNamespace(data='v1:' + 'a'*32 + ':1:1.0'))
        with patch.object(self.module.time, 'monotonic', return_value=3.999):
            self.bridge._check_gesture()
        self.bridge._on_flight_cmd.assert_not_called()
        with patch.object(self.module.time, 'monotonic', return_value=4.):
            for _ in range(100):
                self.bridge._check_gesture()
        self.bridge._on_flight_cmd.assert_called_once()
        self.assertEqual(self.bridge._on_flight_cmd.call_args.args[0].data, 'emergency')
        with patch.object(self.module.time, 'monotonic', return_value=10.):
            self.bridge._on_gesture_heartbeat(SimpleNamespace(data='v1:' + 'a'*32 + ':2:10.0'))
            self.bridge._check_gesture()
        self.bridge._on_flight_cmd.assert_called_once()

    def test_replayed_delayed_or_different_session_cannot_renew(self):
        self.bridge._gesture_timeout = 3.
        self.bridge._on_flight_cmd = Mock()
        with patch.object(self.module.time, 'monotonic', return_value=1.):
            self.bridge._on_gesture_heartbeat(SimpleNamespace(data='v1:' + 'a'*32 + ':1:1.0'))
        for payload in ('v1:' + 'a'*32 + ':1:3.0',
                        'v1:' + 'a'*32 + ':2:1.0',
                        'v1:' + 'b'*32 + ':2:3.0',
                        'v1:' + 'a'*32 + ':2:nan',
                        'v1:' + 'a'*32 + ':2:4.0'):
            with patch.object(self.module.time, 'monotonic', return_value=3.):
                self.bridge._on_gesture_heartbeat(SimpleNamespace(data=payload))
            self.assertEqual(self.bridge._gesture_received, 1.)

    def test_startup_and_unknown_heartbeat_do_not_start_watchdog(self):
        self.bridge._on_flight_cmd = Mock()
        self.bridge._on_gesture_heartbeat(SimpleNamespace(data='other'))
        self.bridge._check_gesture()
        self.bridge._on_flight_cmd.assert_not_called()

    def test_operator_reset_reenables_supervision_without_refreshing_heartbeat(self):
        self.bridge._gesture_received = 1.
        self.bridge._gesture_timeout = 3.
        self.bridge._gesture_loss_sent = self.bridge._link_loss_sent = True
        self.bridge._logic.handle.return_value = (True, 'operator reset confirmed')
        self.bridge._ack_pub = Mock()
        self.bridge._on_flight_cmd = Mock()
        self.bridge._handle('operator_reset')
        with patch.object(self.module.time, 'monotonic', return_value=10.):
            self.bridge._check_gesture()
        self.bridge._on_flight_cmd.assert_called_once()
