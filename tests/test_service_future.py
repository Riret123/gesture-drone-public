import threading
import unittest
from unittest.mock import Mock
from drone_bringup.service_future import wait_response


class ServiceFutureTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.
        self.client, self.future = Mock(), Mock()
        self.future.done.return_value = False
        self.future.exception.return_value = None
        self.future.result.return_value = 'response fixture'
        self.stopping = threading.Event()

    def wait(self, pause=None, clock=None, timeout=.1):
        def advance(seconds):
            self.now += seconds
        return wait_response(self.client, self.future,
                             clock=clock or (lambda: self.now), pause=pause or advance,
                             stopping=self.stopping, timeout=timeout)

    def test_timeout_releases_local_pending_without_retry(self):
        self.assertIsNone(self.wait())
        self.client.remove_pending_request.assert_called_once_with(self.future)
        self.future.cancel.assert_not_called()

    def test_success_and_late_completion_at_observation(self):
        def complete(seconds):
            self.now += seconds
            self.future.done.return_value = True
        self.assertEqual(self.wait(pause=complete), 'response fixture')
        self.client.remove_pending_request.assert_not_called()
        self.future.done.return_value = False
        def late(seconds):
            self.now += 1.
            self.future.done.return_value = True
        self.assertIsNone(self.wait(pause=late))
        self.client.remove_pending_request.assert_called_once()

    def test_stop_and_clock_faults_fail_closed(self):
        for fault in ('stop', 'nan', 'reverse'):
            self.setUp()
            if fault == 'stop':
                self.stopping.set()
                clock = lambda: self.now
            else:
                times = iter((1., float('nan') if fault == 'nan' else 0.))
                clock = lambda: next(times)
            self.assertIsNone(self.wait(clock=clock))
            self.client.remove_pending_request.assert_called_once()

    def test_frozen_clock_and_unrepresentable_deadline_do_not_spin_forever(self):
        pause = Mock()
        self.assertIsNone(self.wait(clock=lambda: 0., pause=pause))
        self.assertLessEqual(pause.call_count, 8)
        self.assertIsNone(self.wait(clock=lambda: 1e308, pause=pause))

    def test_bad_configuration_and_cleanup_failure_never_succeed(self):
        self.client.remove_pending_request.side_effect = RuntimeError('synthetic cleanup failure')
        self.assertIsNone(self.wait())
        for value in (True, 0, 31, float('nan')):
            with self.assertRaises(ValueError):
                self.wait(timeout=value)
