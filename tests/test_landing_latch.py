"""Landing reset, transition matrix, race and deterministic property campaign."""
import random
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from drone_bringup.flight_logic import FlightController
from drone_bringup.service_circuit import ServiceCircuit


class LandingLatchTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.
        self.state = SimpleNamespace(connected=True, armed=False)
        self.calls = Mock(return_value=True)
        self.logic = FlightController(self.calls, lambda: self.state,
                                      clock=lambda: self.now)

    def dwell(self):
        for second in range(6):
            self.now = float(second)
            self.logic.observe_reset_state()

    def test_reset_requires_dwell_then_explicit_confirmation(self):
        self.logic.handle('land')
        self.assertFalse(self.logic.handle('operator_reset')[0])
        self.dwell()
        self.assertFalse(self.logic.handle('open_palm')[0])
        self.assertTrue(self.logic.handle('operator_reset')[0])
        self.assertTrue(self.logic.handle('open_palm')[0])

    def test_broken_dwell_and_clock_anomalies(self):
        for fault in ('armed', 'disconnected', 'gap', 'reverse', 'nan'):
            with self.subTest(fault=fault):
                self.setUp()
                self.logic.handle('land')
                self.dwell()
                if fault == 'armed':
                    self.state.armed = True
                elif fault == 'disconnected':
                    self.state.connected = False
                else:
                    self.now = {'gap': 8., 'reverse': 1., 'nan': float('nan')}[fault]
                self.assertFalse(self.logic.handle('operator_reset')[0])

    def test_land_during_reset_observation_cannot_be_erased(self):
        self.logic.handle('land')
        self.dwell()
        entered, release = threading.Event(), threading.Event()
        def state():
            entered.set()
            self.assertTrue(release.wait(2))
            return self.state
        self.logic.state = state
        reset = threading.Thread(target=self.logic.operator_reset)
        reset.start()
        self.assertTrue(entered.wait(2))
        landed = threading.Thread(target=self.logic.latch_landing)
        landed.start()
        release.set()
        reset.join(2)
        landed.join(2)
        self.assertFalse(reset.is_alive() or landed.is_alive())
        self.assertFalse(self.logic.handle('open_palm')[0])

    def test_random_sequences_never_actuate_takeoff_under_latch(self):
        rng = random.Random(20261109)
        latched = False
        commands = ('open_palm', 'land', 'emergency', 'fist', 'hold', 'other',
                    'operator_reset', 'arm', 'takeoff')
        for _ in range(10000):
            command = rng.choice(commands)
            self.now += .1
            self.state.armed = rng.choice((True, False))
            self.state.connected = rng.choice((True, False))
            self.calls.reset_mock()
            ok, _ = self.logic.handle(command)
            if command in ('land', 'emergency', 'fist'):
                latched = True
            if command == 'operator_reset' and ok:
                latched = False
            if latched:
                for call in self.calls.call_args_list:
                    self.assertNotIn(call.args[0], ('arm', 'takeoff'))
                    self.assertNotEqual(call.args, ('set_mode', 'GUIDED'))


# Explicit independent expected policy, all abstract states x command alphabet.
STATES = ('ready', 'armed', 'disconnected', 'unknown', 'latched', 'latched_armed',
          'reset_eligible')
COMMANDS = ('open_palm', 'fist', 'land', 'emergency', 'hold', 'other',
            'operator_reset', 'arm', 'takeoff', '')


def matrix_case(state_name, command):
    def test(self):
        state = None if state_name == 'unknown' else SimpleNamespace(
            connected=state_name != 'disconnected',
            armed=state_name in ('armed', 'latched_armed'))
        calls = []
        now = [0.]
        logic = FlightController(lambda op, val: calls.append((op, val)) or True,
                                 lambda: state, clock=lambda: now[0])
        latched = state_name.startswith('latched') or state_name == 'reset_eligible'
        if latched:
            logic.latch_landing()
        if state_name == 'reset_eligible':
            for tick in range(6):
                now[0] = float(tick)
                logic.observe_reset_state()
        ok, _ = logic.handle(command)
        expected = []
        if command == 'open_palm':
            if state_name in ('ready', 'armed'):
                expected = [('set_mode', 'GUIDED')]
                if state_name == 'ready':
                    expected += [('arm', True)]
                expected += [('takeoff', 2.)]
                self.assertTrue(ok)
            else:
                self.assertFalse(ok)
        elif command in ('land', 'fist', 'emergency'):
            if state_name not in ('ready', 'latched', 'reset_eligible'):
                expected = [('land', None)]
        elif command == 'hold' and not latched and state_name != 'ready':
            expected = [('set_mode', 'LOITER')]
        elif command == 'operator_reset':
            self.assertEqual(ok, state_name == 'reset_eligible')
        self.assertEqual(calls, expected)
    return test


class CommandMatrixTests(unittest.TestCase):
    pass


for _state in STATES:
    for _index, _command in enumerate(COMMANDS):
        setattr(CommandMatrixTests, f'test_{_state}_{_index}_{_command}',
                matrix_case(_state, _command))


class CircuitTests(unittest.TestCase):
    def test_interruption_releases_inflight_admission(self):
        circuit = ServiceCircuit()
        interrupted = Mock(side_effect=KeyboardInterrupt())
        with self.assertRaises(KeyboardInterrupt):
            circuit.run('land', interrupted)
        self.assertTrue(circuit.run('land', lambda: True))

    def test_one_inflight_per_operation_and_reserved_land(self):
        circuit = ServiceCircuit()
        entered, release = threading.Event(), threading.Event()
        def stalled():
            entered.set()
            return release.wait(2)
        worker = threading.Thread(target=lambda: circuit.run('arm', stalled))
        worker.start()
        try:
            self.assertTrue(entered.wait(2))
            self.assertFalse(circuit.run('arm', lambda: self.fail('parallel arm')))
            self.assertTrue(circuit.run('land', lambda: True))
        finally:
            release.set()
            worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertTrue(circuit.run('arm', lambda: True))

    def test_zero_retry_and_independent_landing_capacity(self):
        circuit = ServiceCircuit()
        failed = Mock(return_value=False)
        for _ in range(100):
            self.assertFalse(circuit.run('arm', failed))
        self.assertEqual(failed.call_count, 3)
        self.assertTrue(circuit.run('land', lambda: True))

    def test_exception_counts_and_success_does_not_clear_failure_budget(self):
        circuit = ServiceCircuit(2)
        failed = Mock(side_effect=RuntimeError('synthetic'))
        self.assertFalse(circuit.run('land', failed))
        self.assertTrue(circuit.run('land', lambda: True))
        self.assertFalse(circuit.run('land', failed))
        self.assertFalse(circuit.run('land', lambda: self.fail('open circuit submitted')))

    def test_invalid_threshold(self):
        for value in (False, 0, -1, 11, 1.5, float('nan')):
            with self.assertRaises(ValueError):
                ServiceCircuit(value)
