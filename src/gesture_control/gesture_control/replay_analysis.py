"""Bounded read-only event analytics; no causal, endurance or flight claims.

Mode dwell attributes each interval to its left endpoint. The final event adds
no inferred duration. Battery drop is a difference in reported percentage points,
not energy consumption. Input events are data and are never executed.
"""
from dataclasses import dataclass
import json
from .validation import finite
from .display_text import bounded_text


@dataclass(frozen=True)
class ReplaySummary:
    count: int
    duration_s: float
    battery_min_percent: float | None
    battery_max_percent: float | None
    battery_change_points: float | None
    mode_transitions: int
    acknowledgement_rows: int
    repeated_timestamps: int
    gap_intervals: tuple
    mode_dwell_s: tuple


def _event(row):
    if type(row) is not dict or set(row) != {'time', 'mode', 'battery', 'ack'}:
        raise ValueError('exact event object required')
    if not finite(row['time']) or row['time'] < 0:
        raise ValueError('invalid event time')
    if not finite(row['battery']) or not 0 <= row['battery'] <= 100:
        raise ValueError('invalid battery percentage')
    for key in ('mode', 'ack'):
        value = row[key]
        if not bounded_text(value, 1 if key == 'mode' else 0, 256):
            raise ValueError('invalid bounded event text')
    return dict(row)


def _limits(max_events, gap_s):
    if type(max_events) is not int or not 1 <= max_events <= 100000:
        raise ValueError('max_events must be an integer in [1,100000]')
    if not finite(gap_s) or gap_s <= 0:
        raise ValueError('positive finite gap threshold required')


def analyze_events(events, *, gap_s, max_events=10000):
    """Aggregate chronological events within explicit resource/analysis bounds.

    Exactly gap_s is reported as a gap. Duplicate timestamps are counted without
    division. A raised error yields no partial report to mistake for complete data.
    """
    _limits(max_events, gap_s)
    count = transitions = acknowledgements = duplicates = 0
    first = previous = None
    low = high = None
    gaps = []
    dwell = {}
    for raw in events:
        if count >= max_events:
            raise ValueError('event budget exceeded')
        row = _event(raw)
        if previous is not None:
            delta = row['time'] - previous['time']
            if delta < 0:
                raise ValueError('events must be chronological')
            if delta == 0:
                duplicates += 1
            if delta >= gap_s:
                gaps.append((previous['time'], row['time']))
            dwell[previous['mode']] = dwell.get(previous['mode'], 0.) + delta
            if not finite(dwell[previous['mode']]):
                raise ValueError('duration overflow')
            transitions += row['mode'] != previous['mode']
        else:
            first = row
        count += 1
        acknowledgements += bool(row['ack'])
        low = row['battery'] if low is None else min(low, row['battery'])
        high = row['battery'] if high is None else max(high, row['battery'])
        previous = row
    if first is None:
        return ReplaySummary(0, 0., None, None, None, 0, 0, 0, (), ())
    duration = previous['time'] - first['time']
    if not finite(duration):
        raise ValueError('duration overflow')
    return ReplaySummary(count, duration, low, high,
                         previous['battery'] - first['battery'], transitions,
                         acknowledgements, duplicates, tuple(gaps),
                         tuple(sorted(dwell.items())))


def read_jsonl(stream, *, max_events=10000, max_line_bytes=16384):
    """Yield strict bounded JSONL events from a text or binary readline stream.

    Blank lines, duplicate fields and nonstandard constants reject. Readers are
    caller-owned and are neither opened nor closed here. No log text is executed.
    """
    _limits(max_events, 1)
    if type(max_line_bytes) is not int or not 1 <= max_line_bytes <= 1048576:
        raise ValueError('invalid line byte limit')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate event field')
            result[key] = value
        return result
    def reject_constant(value):
        raise ValueError('nonstandard JSON number')
    count = 0
    previous_time = None
    while True:
        line = stream.readline(max_line_bytes + 1)
        if line in ('', b''):
            break
        if count >= max_events or type(line) not in (str, bytes):
            raise ValueError('event budget or reader contract violation')
        try:
            if type(line) is bytes:
                if len(line) > max_line_bytes:
                    raise ValueError('event line too large')
                line = line.decode('utf-8', errors='strict')
            if len(line.encode('utf-8')) > max_line_bytes:
                raise ValueError('event line too large')
            row = _event(json.loads(line, object_pairs_hook=unique,
                                    parse_constant=reject_constant))
        except (UnicodeError, RecursionError) as exc:
            raise ValueError('invalid event encoding or nesting') from exc
        if previous_time is not None and row['time'] < previous_time:
            raise ValueError('events must be chronological')
        previous_time = row['time']
        count += 1
        yield row
