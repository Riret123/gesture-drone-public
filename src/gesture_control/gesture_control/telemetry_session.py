"""Read-only single-session receive ownership and replay rejection experiment.

Sequence/session metadata is caller-provided, not authenticated. No transport,
flight authority, FC freshness guarantee or deadman actuation is implemented.
"""
import re
from .telemetry_contract import TelemetryView, normalize_telemetry
from .validation import finite


class TelemetrySession:
    """A fresh instance is required for a new externally established session.

    An invalid packet immediately clears the displayed sample. Rejected packets
    never renew its receive time or consume sequence numbers. Times must be local
    monotonic observations; exact equality is allowed for deterministic batches.
    """
    def __init__(self, session_id, max_age):
        if (type(session_id) is not str
                or re.fullmatch(r'[A-Za-z0-9_-]{1,64}', session_id) is None):
            raise ValueError('bounded ASCII session identifier required')
        if not finite(max_age) or max_age <= 0:
            raise ValueError('positive finite max_age required')
        self.session_id = session_id
        self.max_age = max_age
        self._sequence = -1
        self._clock = None
        self._received = None
        self._payload = None

    def _advance(self, now):
        if (not finite(now) or now < 0
                or self._clock is not None and now < self._clock):
            self._payload = None
            raise ValueError('nonnegative monotonic local time required')
        self._clock = now

    def receive(self, session_id, sequence, payload, now):
        self._advance(now)
        if (type(session_id) is not str or session_id != self.session_id
                or type(sequence) is not int or not 0 <= sequence <= 2**63-1
                or sequence <= self._sequence):
            self._payload = None
            return TelemetryView('INVALID')
        view = normalize_telemetry(payload, now, now, self.max_age)
        if view.status not in ('MOCK', 'RECEIVED'):
            self._payload = None
            return view
        # Own a normalized, immutable-content snapshot rather than aliasing caller data.
        self._payload = dict(schema=1, mock=view.status == 'MOCK', age=payload['age'],
                             mode=view.mode, battery=view.battery_percent,
                             deadman=view.deadman, acks=list(view.acknowledgements))
        self._sequence = sequence
        self._received = now
        return view

    def view(self, now):
        self._advance(now)
        if self._payload is None:
            return TelemetryView('OFFLINE')
        return normalize_telemetry(self._payload, self._received, now, self.max_age)
