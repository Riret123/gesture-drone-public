"""Bound local diagnostic child time and captured output before allocation growth."""
import os
import subprocess
import threading
import time
from .state_watchdog import _finite


def run_probe(argv, *, timeout=8., max_bytes=16384):
    if (not isinstance(argv, (list, tuple)) or not argv
            or any(not isinstance(arg, str) or '\x00' in arg for arg in argv)
            or not _finite(timeout) or not 0 < timeout <= 60
            or type(max_bytes) is not int or not 1 <= max_bytes <= 1_048_576):
        raise ValueError('invalid bounded probe arguments')
    output = bytearray()
    finished, exceeded = threading.Event(), threading.Event()
    process = None
    reader = None
    try:
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, bufsize=0,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

        def read_output():
            try:
                while True:
                    chunk = process.stdout.read(min(4096, max_bytes + 1 - len(output)))
                    if not chunk:
                        break
                    output.extend(chunk)
                    if len(output) > max_bytes:
                        exceeded.set()
                        break
            except (OSError, ValueError):
                exceeded.set()
            finally:
                finished.set()

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        deadline = time.monotonic() + timeout
        while not (finished.is_set() and process.poll() is not None):
            if exceeded.is_set() or time.monotonic() >= deadline:
                return 2, ''
            finished.wait(.02)
            if finished.is_set() and process.poll() is None:
                time.sleep(.01)
        if exceeded.is_set():
            return 2, ''
        return process.returncode, output.decode('utf-8', errors='strict')
    except (OSError, UnicodeError, RuntimeError):
        return 2, ''
    finally:
        if process is not None:
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass
            try:
                process.wait(timeout=1.)
            except (OSError, subprocess.TimeoutExpired):
                pass
            if process.stdout is not None:
                try:
                    process.stdout.close()
                except OSError:
                    pass
        if reader is not None and reader.ident is not None:
            reader.join(timeout=1.)
