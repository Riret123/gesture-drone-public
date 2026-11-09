"""Replay-resistant local rover session, with stopped-state reset and watchdog."""
from .protocol import decode
from .freshness import Freshness
from .rover import wheels


class RoverSession:
    def __init__(self, timeout: float = .5):
        self.gate = Freshness(timeout)
        self.sequence = -1
        self.output = (0., 0.)

    def accept(self, raw: bytes, now: float) -> bool:
        # Time validation happens even for rejected messages, never renewing lease.
        self.gate.fresh(now)
        try:
            packet = decode(raw)
        except (ValueError, TypeError):
            return False
        if packet['seq'] <= self.sequence:
            return False
        self.sequence = packet['seq']
        self.output = ((0., 0.) if packet['mode'] == 'hold' else
                       wheels(packet['linear'], packet['angular']))
        self.gate.receive(now)
        return True

    def poll(self, now: float) -> tuple[float, float]:
        if not self.gate.fresh(now):
            self.output = (0., 0.)
        return self.output

    def reset(self, now: float) -> None:
        if self.poll(now) != (0., 0.):
            raise ValueError('stop before resetting sequence session')
        self.sequence = -1
        self.gate.received = None
