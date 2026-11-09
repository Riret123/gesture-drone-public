"""Strict read-only telemetry normalization. No ROS, transport or actuation.

Times are local monotonic receive times supplied by the caller; source-reported
age is additional, never a replacement for measuring local transport silence.
"""
from dataclasses import dataclass
import json
from .validation import finite
from .display_text import bounded_text


def _number(value):
    return finite(value)


def decode_telemetry(source, received_at, now, max_age, *, max_bytes=16384):
    """Bounded strict UTF-8 JSON ingestion; malformed data becomes INVALID.

    max_bytes is a parser resource limit, not a transport-level allocation guard.
    The caller must bound incoming reads before allocating the input object.
    """
    if type(max_bytes) is not int or not 1 <= max_bytes <= 1048576:
        raise ValueError('max_bytes must be an integer between 1 and 1048576')
    if not _number(max_age) or max_age <= 0:
        raise ValueError('max_age must be a positive finite number')
    if type(source) not in (str, bytes) or len(source) > max_bytes:
        return TelemetryView('INVALID')
    try:
        if type(source) is bytes:
            source = source.decode('utf-8', errors='strict')
        if len(source.encode('utf-8')) > max_bytes:
            return TelemetryView('INVALID')
        def unique(pairs):
            output = {}
            for key, value in pairs:
                if key in output:
                    raise ValueError('duplicate field')
                output[key] = value
            return output
        def reject_constant(value):
            raise ValueError('nonstandard number')
        payload = json.loads(source, object_pairs_hook=unique,
                             parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        return TelemetryView('INVALID')
    return normalize_telemetry(payload, received_at, now, max_age)


@dataclass(frozen=True)
class TelemetryView:
    status: str
    mode: str | None = None
    battery_percent: float | None = None
    deadman: bool | None = None
    acknowledgements: tuple[str, ...] = ()


def normalize_telemetry(payload, received_at, now, max_age):
    """Return unknown values on any invalid envelope; never authorize flight.

    Exact fields prevent accidentally treating a different schema as telemetry.
    Equality at the caller-selected freshness limit is stale. No operational
    freshness default is imposed by this offline experiment.
    """
    if not _number(max_age) or max_age <= 0:
        raise ValueError('max_age must be a positive finite number')
    if not _number(now) or not _number(received_at) or now < received_at:
        return TelemetryView('INVALID')
    fields = {'schema', 'mock', 'age', 'mode', 'battery', 'deadman', 'acks'}
    if type(payload) is not dict or set(payload) != fields:
        return TelemetryView('INVALID')
    if (type(payload['schema']) is not int or payload['schema'] != 1
            or type(payload['mock']) is not bool
            or not _number(payload['age']) or payload['age'] < 0
            or not bounded_text(payload['mode'], 1, 64)
            or not _number(payload['battery']) or not 0 <= payload['battery'] <= 100
            or type(payload['deadman']) is not bool
            or type(payload['acks']) is not list or len(payload['acks']) > 30
            or any(not bounded_text(a, 0, 256) for a in payload['acks'])):
        return TelemetryView('INVALID')
    if now - received_at + payload['age'] >= max_age:
        return TelemetryView('STALE')
    return TelemetryView('MOCK' if payload['mock'] else 'RECEIVED',
                         payload['mode'], float(payload['battery']),
                         payload['deadman'], tuple(payload['acks']))
