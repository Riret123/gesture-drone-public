"""Actual adapters joined in memory; no ROS, camera, FC, sockets or motor power."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_bridge_adapter import load_adapter
from test_gesture_adapter import adapter
from test_core_chain import hand
from drone_bringup.command_admission import CommandAdmission
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog
from gesture_control.safety import GestureSafety


class InlineWorker:
    def __init__(self, target, args, daemon):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


class ActualAdapterChainTests(unittest.TestCase):
    def test_landmarks_publish_services_confirmations_and_acknowledgements(self):
        gm, bm = adapter(), load_adapter()
        clock = [0.]
        state = SimpleNamespace(connected=True, armed=False, mode='STABILIZE')
        bridge = bm.FlightCmdBridge.__new__(bm.FlightCmdBridge)
        bridge._stopping = threading.Event()
        bridge._service_wait = bridge._service_timeout = bridge._transition_timeout = 5.
        bridge._state_watchdog = StateWatchdog(lambda: clock[0])
        bridge._state_watchdog.receive(state)
        bridge._admission = CommandAdmission()
        bridge._ack_pub = Mock()
        bridge._logic = FlightController(bridge._call, bridge._state_watchdog.current,
                                         confirm=bridge._confirm)
        calls = []
        def service(operation):
            def submit(request):
                calls.append(operation)
                if operation == 'set_mode':
                    state.mode = request.custom_mode
                elif operation == 'arm':
                    state.armed = request.value
                bridge._state_watchdog.receive(state)
                future = Mock()
                future.done.return_value = True
                future.exception.return_value = None
                future.result.return_value = SimpleNamespace(success=True, mode_sent=True)
                return future
            client = Mock()
            client.wait_for_service.return_value = True
            client.call_async.side_effect = submit
            return client
        bridge._clients = {operation: service(operation)
                           for operation in ('set_mode', 'arm', 'takeoff', 'land')}
        gesture = gm.GestureNode.__new__(gm.GestureNode)
        gesture._safety = GestureSafety(frames=2)
        gesture._curl_ratio = 1.1
        gesture._cap = Mock()
        gesture._cap.read.return_value = (True, object())
        gesture._hands = Mock()
        gesture._hands.process.return_value = SimpleNamespace(
            multi_hand_landmarks=[SimpleNamespace(landmark=hand(True))])
        gesture._publisher = Mock()
        gesture._publisher.publish.side_effect = bridge._on_flight_cmd
        gm.cv2.flip = lambda frame, axis: frame
        gm.cv2.COLOR_BGR2RGB = 1
        gm.cv2.cvtColor = lambda *args: SimpleNamespace(flags=SimpleNamespace(writeable=True))
        with patch.object(bm.threading, 'Thread', InlineWorker), \
                patch.object(bm.time, 'monotonic', side_effect=lambda: clock[0]):
            for now in (.1, .2):
                clock[0] = now
                gesture._on_timer()
            self.assertEqual(calls, ['set_mode', 'arm', 'takeoff'])
            self.assertTrue(state.armed)
            self.assertEqual(state.mode, 'GUIDED')
            self.assertIn('open_palm:OK:', bridge._ack_pub.publish.call_args.args[0].data)
            gesture._cap.read.return_value = (False, None)
            clock[0] = 2.2
            gesture._on_timer()
            self.assertEqual(state.mode, 'LOITER')
            clock[0] = 5.2
            gesture._on_timer()
        self.assertEqual(calls[-1], 'land')
        self.assertIn('land:OK:', bridge._ack_pub.publish.call_args.args[0].data)
        self.assertEqual([c.args[0].data for c in gesture._publisher.publish.call_args_list],
                         ['open_palm', 'hold', 'land'])
