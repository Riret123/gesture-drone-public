"""Harmless local Python children; no ROS, camera, FC or network probes."""
import sys
import time
import unittest
import subprocess
from unittest.mock import patch
from drone_bringup.bounded_probe import run_probe


class BoundedProbeTests(unittest.TestCase):
    def test_reader_thread_start_failure_reaps_owned_child(self):
        original = subprocess.Popen
        children = []
        def launch(*args, **kwargs):
            process = original(*args, **kwargs)
            children.append(process)
            return process
        with patch('drone_bringup.bounded_probe.subprocess.Popen', side_effect=launch), \
                patch('drone_bringup.bounded_probe.threading.Thread.start',
                      side_effect=RuntimeError('synthetic thread start failure')):
            self.assertEqual(run_probe((sys.executable, '-c', 'import time; time.sleep(30)')),
                             (2, ''))
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)

    def test_stdout_and_stderr_share_bound(self):
        status, output = run_probe((sys.executable, '-c',
                                   'import sys; print("out"); print("err", file=sys.stderr)'))
        self.assertEqual(status, 0)
        self.assertIn('out', output)
        self.assertIn('err', output)

    def test_output_overflow_fails_without_partial_success(self):
        for stream in ('stdout', 'stderr'):
            status, output = run_probe((sys.executable, '-c',
                                       f'import sys; sys.{stream}.write("x"*1000000)'), max_bytes=100)
            self.assertEqual((status, output), (2, ''))

    def test_hanging_child_is_terminated(self):
        started = time.monotonic()
        self.assertEqual(run_probe((sys.executable, '-c', 'import time; time.sleep(30)'),
                                   timeout=.2), (2, ''))
        self.assertLess(time.monotonic() - started, 5.)

    def test_nonzero_and_invalid_encoding(self):
        self.assertEqual(run_probe((sys.executable, '-c', 'raise SystemExit(7)')),
                         (7, ''))
        self.assertEqual(run_probe((sys.executable, '-c',
                                   'import sys; sys.stdout.buffer.write(bytes([255]))')), (2, ''))

    def test_bad_limits_reject_before_launch(self):
        for kwargs in ({'timeout': True}, {'timeout': float('nan')},
                       {'timeout': 61}, {'max_bytes': False}, {'max_bytes': 0}):
            with self.assertRaises(ValueError):
                run_probe(('unused',), **kwargs)
