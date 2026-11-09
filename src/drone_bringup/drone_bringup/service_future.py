"""Bounded response polling and local pending-request release, no FC cancellation."""
from .state_watchdog import _finite
import math


def wait_response(client, future, *, clock, pause, stopping, timeout):
    """Return accepted transport response or None; release abandoned local future.

    remove_pending_request only releases local correlation/storage. It neither
    recalls a command already sent nor proves the FC did not execute it. A native
    client method that itself blocks cannot be interrupted by this Python timer.
    """
    abandoned = True
    try:
        if not _finite(timeout) or not .1 <= timeout <= 30:
            raise ValueError('response timeout must be in [0.1,30]')
        started = clock()
        if not _finite(started) or started < 0:
            return None
        deadline = started + timeout
        if not _finite(deadline) or deadline <= started:
            return None
        previous = started
        polls = 0
        max_polls = math.ceil(timeout / .02) + 2
        while not future.done():
            now = clock()
            if (stopping.is_set() or not _finite(now) or now < previous
                    or now >= deadline or polls >= max_polls):
                return None
            polls += 1
            previous = now
            pause(.02)
        now = clock()
        if (stopping.is_set() or not _finite(now) or now < previous
                or now > deadline or future.exception() is not None):
            return None
        response = future.result()
        abandoned = False
        return response
    finally:
        if abandoned:
            try:
                client.remove_pending_request(future)
            except Exception:
                pass  # Local cleanup failure cannot turn an uncertain call into success.
