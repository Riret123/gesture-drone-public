"""640 combined admission/FC/latch/command subcases against actual bridge entry."""
import itertools
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import test_bridge_adapter as fixture
from test_core_ros_chain import InlineWorker
from drone_bringup.command_admission import CommandAdmission
from drone_bringup.flight_logic import FlightController
from drone_bringup.service_circuit import ServiceCircuit
from drone_bringup.state_watchdog import StateWatchdog


COMMANDS = ('open_palm', 'hold', 'fist', 'land', 'emergency', 'other', 'operator_reset', 'unknown')
FC_STATES = (None, (False, False), (False, True), (True, False), (True, True))


def expected_services(occupied, state, latched, command):
    connected, armed = state if state is not None else (False, None)
    if command in ('fist', 'land', 'emergency'):
        return [] if 'land' in occupied or connected and armed is False else [('land', None)]
    if command == 'hold':
        if latched or occupied & {'land', 'hold'} or connected and armed is False:
            return []
        return [('set_mode', 'LOITER')]
    if command == 'open_palm':
        if latched or occupied or not connected:
            return []
        return ([('set_mode', 'GUIDED')] + ([] if armed else [('arm', True)])
                + [('takeoff', 2.)])
    return []


class CombinedCommandMatrixTests(unittest.TestCase):
    def test_all_640_combined_entry_cells(self):
        module = fixture.load_adapter()
        cells = 0
        with patch.object(module.time, 'monotonic', return_value=0.), \
                patch.object(module.threading, 'Thread', InlineWorker):
            for bits, fc, latched, command in itertools.product(
                    itertools.product((False, True), repeat=3), FC_STATES,
                    (False, True), COMMANDS):
                occupied = {lane for lane, enabled in zip(('takeoff', 'hold', 'land'), bits) if enabled}
                with self.subTest(lanes=sorted(occupied), fc=fc, latched=latched, command=command):
                    bridge = module.FlightCmdBridge.__new__(module.FlightCmdBridge)
                    bridge._stopping = threading.Event()
                    bridge._service_wait = bridge._service_timeout = bridge._transition_timeout = 5.
                    bridge._state_watchdog = StateWatchdog(lambda: 0.)
                    state = None if fc is None else SimpleNamespace(
                        connected=fc[0], armed=fc[1], mode='STABILIZE')
                    if state is not None:
                        bridge._state_watchdog.receive(state)
                    bridge._logic = FlightController(
                        bridge._call, bridge._state_watchdog.current,
                        confirm=bridge._confirm, clock=lambda: 0., startup_latched=latched)
                    bridge._circuit = ServiceCircuit()
                    bridge._admission = CommandAdmission()
                    for lane, name in (('takeoff', 'open_palm'), ('hold', 'hold'), ('land', 'land')):
                        if lane in occupied:
                            self.assertIsNotNone(bridge._admission.acquire(name))
                    bridge._ack_pub = Mock()
                    trace = []
                    def client_for(operation):
                        client = Mock()
                        client.wait_for_service.return_value = True
                        client.service_is_ready.return_value = True
                        def submit(request):
                            value = (request.custom_mode if operation == 'set_mode' else
                                     request.value if operation == 'arm' else
                                     request.altitude if operation == 'takeoff' else None)
                            trace.append((operation, value))
                            if state is not None:
                                if operation == 'set_mode':
                                    state.mode = value
                                elif operation == 'arm':
                                    state.armed = value
                                bridge._state_watchdog.receive(state)
                            future = Mock()
                            future.done.return_value = True
                            future.exception.return_value = None
                            future.result.return_value = SimpleNamespace(success=True, mode_sent=True)
                            return future
                        client.call_async.side_effect = submit
                        return client
                    bridge._clients = {name: client_for(name)
                                       for name in ('set_mode', 'arm', 'takeoff', 'land')}
                    bridge._on_flight_cmd(SimpleNamespace(data=command))
                    self.assertEqual(trace, expected_services(occupied, fc, latched, command))
                    self.assertEqual(set(bridge._admission._leases), occupied)
                    self.assertTrue(bridge._ack_pub.publish.called)
                    if latched or command in ('fist', 'land', 'emergency'):
                        before = trace[:]
                        self.assertFalse(bridge._logic.handle('open_palm')[0])
                        self.assertEqual(trace, before)
                    cells += 1
        self.assertEqual(cells, 640)
