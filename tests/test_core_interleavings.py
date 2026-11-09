"""Deterministic threaded and service-boundary cancellation campaigns."""
import threading
from types import SimpleNamespace
import unittest
from drone_bringup.flight_logic import FlightController


class CoreInterleavingTests(unittest.TestCase):
    def test_emergency_while_guided_response_pending(self):
        entered, release = threading.Event(), threading.Event()
        calls, outcome = [], []
        state = SimpleNamespace(connected=True, armed=False)
        def service(name, value):
            calls.append((name, value))
            if name == 'set_mode' and value == 'GUIDED':
                entered.set()
                if not release.wait(2.):
                    return False
            return True
        logic = FlightController(service, lambda: state)
        worker = threading.Thread(target=lambda: outcome.append(logic.handle('open_palm')))
        worker.start()
        try:
            self.assertTrue(entered.wait(2.))
            logic.handle('emergency')
        finally:
            release.set()
            worker.join(2.)
        self.assertFalse(worker.is_alive())
        self.assertFalse(outcome[0][0])
        self.assertNotIn(('arm', True), calls)
        self.assertNotIn(('takeoff', 2.), calls)

    def test_every_takeoff_service_boundary_with_safety_commands(self):
        for initial_armed in (False, True):
            operations = ['set_mode', 'takeoff'] if initial_armed else ['set_mode', 'arm', 'takeoff']
            for interrupted in operations:
                for safety in ('hold', 'land', 'emergency'):
                    with self.subTest(armed=initial_armed, step=interrupted, safety=safety):
                        state = SimpleNamespace(connected=True, armed=initial_armed)
                        calls = []
                        injected = [False]
                        def service(name, value):
                            calls.append((name, value))
                            if name == 'arm':
                                state.armed = True
                            if name == interrupted and not injected[0]:
                                injected[0] = True
                                logic.handle(safety)
                            return True
                        logic = FlightController(service, lambda: state)
                        logic.handle('open_palm')
                        index = next(i for i, pair in enumerate(calls) if pair[0] == interrupted)
                        following_takeoff_steps = [name for name, value in calls[index+1:]
                                                   if name in ('arm', 'takeoff')
                                                   or name == 'set_mode' and value == 'GUIDED']
                        self.assertEqual(following_takeoff_steps, [])

    def test_safety_exception_releases_active_guard(self):
        state = SimpleNamespace(connected=True, armed=True)
        def service(name, value):
            if name == 'land':
                raise RuntimeError('synthetic adapter failure')
            return True
        logic = FlightController(service, lambda: state)
        with self.assertRaises(RuntimeError):
            logic.handle('land')
        # The error must not leak locks or active-worker counters forever.
        self.assertEqual(logic._safety_active, 0)
        self.assertFalse(logic._land_lock.locked())
        self.assertFalse(logic.handle('open_palm')[0])
        self.assertIn('landing latch', logic.handle('open_palm')[1])
