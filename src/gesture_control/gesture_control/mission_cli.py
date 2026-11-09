"""Read a bounded local mission and print toy simulation JSON. No send mode.

Installed usage: python -m gesture_control.mission_cli plan.json --summary-only
For stdin use `-`; JSON input is UTF-8. This never imports or contacts ROS.
"""
import argparse
import json
import sys

from .mission_schema import MAX_BYTES, Mission, number
from .mission_simulation import Trajectory


def evaluate(source, interval=0.1, max_duration=3600, max_samples=10000,
             summary_only=False):
    """Pure evaluation facade suitable for a view-only UI or unittest."""
    if type(summary_only) is not bool:
        raise ValueError('summary_only must be boolean')
    number(interval, 'interval', 0.001, 3600)
    if type(max_samples) is not int or not 1 <= max_samples <= 100000:
        raise ValueError('max_samples must be integer in [1, 100000]')
    mission = Mission.from_json(source)
    trajectory = Trajectory(mission, max_duration=max_duration)
    report = {'schema': 'offline_mission_report_v1', 'summary': trajectory.summary()}
    if not summary_only:
        rows = trajectory.samples(interval, max_samples)
        report['samples'] = [{'time_s': row.time, 'enu_m': list(row.position),
                              'waypoint': row.waypoint, 'phase': row.phase} for row in rows]
    return report


def read_bounded(stream):
    """Read at most limit+1 bytes from an explicitly supplied binary stream."""
    chunks = []
    received = 0
    while True:
        chunk = stream.read(MAX_BYTES + 1 - received)
        if type(chunk) is not bytes:
            raise ValueError('input must be binary UTF-8 data')
        if not chunk:
            break
        chunks.append(chunk)
        received += len(chunk)
        if received > MAX_BYTES:
            raise ValueError('input exceeds mission byte budget')
    data = b''.join(chunks)
    try:
        return data.decode('utf-8')
    except UnicodeError as exc:
        raise ValueError('input is not UTF-8') from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline toy ENU mission simulator; no flight transport')
    parser.add_argument('input', help='UTF-8 mission JSON path, or - for stdin')
    parser.add_argument('--interval', type=float, default=.1, help='sample interval seconds (default .1)')
    parser.add_argument('--max-duration', type=float, default=3600, help='offline duration budget seconds')
    parser.add_argument('--max-samples', type=int, default=10000, help='bounded output sample count')
    parser.add_argument('--summary-only', action='store_true', help='omit timeline output')
    args = parser.parse_args(argv)
    try:
        if args.input == '-':
            source = read_bounded(sys.stdin.buffer)
        else:
            with open(args.input, 'rb') as stream:
                source = read_bounded(stream)
        report = evaluate(source, args.interval, args.max_duration, args.max_samples,
                          args.summary_only)
    except (ValueError, OSError) as exc:
        # Do not echo mission payloads, full filenames or arbitrary OS messages.
        category = 'input_io_error' if isinstance(exc, OSError) else 'invalid_offline_mission'
        print(json.dumps({'error': category, 'flight_validated': False}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
