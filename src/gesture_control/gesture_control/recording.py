"""Small allowlisted flight event recorder; replay is data only, never commands."""
import csv
import json
import math

FIELDS = ('time', 'mode', 'battery', 'ack')


def validate(event: dict) -> dict:
    if set(event) != set(FIELDS):
        raise ValueError('exact event fields required; do not log credentials')
    time, battery = float(event['time']), float(event['battery'])
    if not math.isfinite(time) or time < 0 or not math.isfinite(battery):
        raise ValueError('invalid numeric event')
    if not 0 <= battery <= 100:
        raise ValueError('invalid battery')
    if any(not isinstance(event[k], str) or len(event[k]) > 256
           for k in ('mode', 'ack')):
        raise ValueError('invalid text field')
    return dict(time=time, mode=event['mode'], battery=battery, ack=event['ack'])


def record(stream, events, format: str = 'jsonl') -> int:
    if format not in ('jsonl', 'csv'):
        raise ValueError('format must be jsonl or csv')
    writer = csv.DictWriter(stream, FIELDS) if format == 'csv' else None
    if writer:
        writer.writeheader()
    count = 0
    previous = -1.
    for event in events:
        row = validate(event)
        if row['time'] < previous:
            raise ValueError('events must be chronological')
        previous = row['time']
        if writer:
            writer.writerow(row)
        else:
            stream.write(json.dumps(row, allow_nan=False) + '\n')
        count += 1
    return count


def replay(stream, format: str = 'jsonl'):
    if format not in ('jsonl', 'csv'):
        raise ValueError('invalid format')
    rows = csv.DictReader(stream) if format == 'csv' else (json.loads(s) for s in stream)
    previous = -1.
    for row in rows:
        event = validate(row)
        if event['time'] < previous:
            raise ValueError('out of order replay')
        previous = event['time']
        yield event
