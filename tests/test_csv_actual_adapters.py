"""CSV -> actual camera callback -> actual bridge -> fake MAVROS, fully inert."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import test_bridge_adapter as bridge_fixture
import test_gesture_adapter as gesture_fixture
from test_bridge_startup_inhibition import InertNode
from test_core_ros_chain import InlineWorker
from drone_bringup.deterministic_replay import read_landmark_csv
from gesture_control.safety import GestureSafety


class CsvActualAdapterTests(unittest.TestCase):
    def test_csv_flight_after_explicit_startup_reset_then_latched_rejection(self):
        gm = gesture_fixture.adapter()
        bm = bridge_fixture.load_adapter(InertNode)
        now = [0.]
        state = SimpleNamespace(connected=True, armed=False, mode='STABILIZE')
        calls = []
        with patch.object(bm.time, 'monotonic', side_effect=lambda: now[0]), \
                patch.object(gm.time, 'perf_counter', return_value=0.), \
                patch.object(bm.threading, 'Thread', InlineWorker):
            bridge = bm.FlightCmdBridge()
            for tick in range(6):
                now[0] = float(tick)
                bridge._on_state(state)
                bridge._check_link()
            bridge._handle('operator_reset')
            self.assertIn('operator_reset:OK:', bridge._ack_pub.publish.call_args.args[0].data)
            def fake_client(operation):
                client = Mock()
                client.wait_for_service.return_value = True
                def submit(request):
                    calls.append(operation)
                    if operation == 'set_mode':
                        state.mode = request.custom_mode
                    elif operation == 'arm':
                        state.armed = request.value
                    elif operation == 'land':
                        state.mode = 'LAND'
                    bridge._on_state(state)
                    future = Mock()
                    future.done.return_value = True
                    future.exception.return_value = None
                    future.result.return_value = SimpleNamespace(success=True, mode_sent=True)
                    return future
                client.call_async.side_effect = submit
                return client
            bridge._clients = {name: fake_client(name) for name in ('set_mode', 'arm', 'takeoff', 'land')}
            gesture = gm.GestureNode.__new__(gm.GestureNode)
            gesture._safety = GestureSafety(frames=2, now=5.)
            gesture._curl_ratio = 1.1
            gesture._pose_profile = None
            gesture._cap, gesture._hands = Mock(), Mock()
            gesture._cap.read.return_value = (True, object())
            gesture._publisher = Mock()
            gesture._publisher.publish.side_effect = bridge._on_flight_cmd
            gesture._heartbeat_pub = Mock()
            gesture._heartbeat_pub.publish.side_effect = bridge._on_gesture_heartbeat
            gesture._heartbeat_session = 'c' * 32
            gesture._heartbeat_seq = 0
            gm.cv2.flip = lambda frame, axis: frame
            gm.cv2.COLOR_BGR2RGB = 1
            gm.cv2.cvtColor = lambda *args: SimpleNamespace(flags=SimpleNamespace(writeable=True))
            path = Path(__file__).parent / 'fixtures/core_landmarks_synthetic.csv'
            for frame in read_landmark_csv(path.read_text()):
                now[0] = 6. + frame.time
                gesture._hands.process.return_value = SimpleNamespace(multi_hand_landmarks=[
                    SimpleNamespace(landmark=[SimpleNamespace(x=x, y=y, z=z) for x, y, z in hand])
                    for hand in frame.hands])
                gesture._on_timer()
                bridge._check_link()
            self.assertEqual(calls, ['set_mode', 'arm', 'takeoff', 'land'])
            self.assertTrue(state.armed)  # Service ACK does not assert touchdown.
            bridge._on_flight_cmd(SimpleNamespace(data='open_palm'))
            self.assertIn('open_palm:FAIL:', bridge._ack_pub.publish.call_args.args[0].data)
            self.assertEqual(calls, ['set_mode', 'arm', 'takeoff', 'land'])
            self.assertEqual(gesture._heartbeat_pub.publish.call_count, 4)
            bridge.destroy_node()
