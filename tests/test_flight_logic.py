import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, call
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/drone_bringup'))
from drone_bringup.flight_logic import FlightController


class FlightTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock(return_value=True)
        self.state = SimpleNamespace(armed=False, connected=True)
        self.logic = FlightController(self.service, lambda: self.state)

    def test_order(self):
        self.assertTrue(self.logic.handle('open_palm')[0])
        self.assertEqual(self.service.call_args_list,
                         [call('set_mode', 'GUIDED'), call('arm', True), call('takeoff', 2.0)])

    def test_arm_guard(self):
        self.state.armed = True
        self.logic.handle('open_palm')
        self.assertNotIn(call('arm', True), self.service.call_args_list)

    def test_land_guard_and_emergency(self):
        self.logic.handle('fist')
        self.service.assert_not_called()
        self.state.armed = True
        for command in ('fist', 'land', 'emergency'):
            self.assertTrue(self.logic.handle(command)[0])
        self.assertEqual(self.service.call_args_list, [call('land', None)] * 3)

    def test_unknown_state(self):
        self.state = None
        self.assertFalse(self.logic.handle('open_palm')[0])
        self.logic.handle('emergency')
        self.service.assert_called_once_with('land', None)

    def test_hold_and_noop(self):
        self.state.armed = True
        self.logic.handle('hold')
        self.service.assert_called_once_with('set_mode', 'LOITER')
        self.logic.handle('other')
        self.assertEqual(self.service.call_count, 1)

    def test_failures_stop_sequence(self):
        for results, count in (([False], 1), ([True, False], 2), ([True, True, False], 3)):
            self.service.reset_mock()
            self.service.side_effect = results
            self.assertFalse(self.logic.handle('open_palm')[0])
            self.assertEqual(self.service.call_count, count)

    def test_safety_preempts_pending_takeoff(self):
        def service(name, value):
            if name == 'set_mode' and value == 'GUIDED':
                self.logic.handle('emergency')
            return True
        self.service.side_effect = service
        self.assertFalse(self.logic.handle('open_palm')[0])
        self.assertNotIn(call('arm', True), self.service.call_args_list)

    def test_duplicate_in_progress(self):
        self.logic._takeoff_lock.acquire()
        try:
            self.assertIn('SKIP', self.logic.handle('open_palm')[1])
            self.service.assert_not_called()
        finally:
            self.logic._takeoff_lock.release()
