"""Read a bounded local JSONL log and print aggregate offline metrics only."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.replay_analysis import analyze_events, read_jsonl


def main(argv=None, *, opener=open, output=None, errors=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--gap', type=float, required=True,
                        help='explicit analysis gap threshold in seconds')
    parser.add_argument('--max-events', type=int, default=10000)
    parser.add_argument('--max-line-bytes', type=int, default=16384)
    args = parser.parse_args(argv)
    output = sys.stdout if output is None else output
    errors = sys.stderr if errors is None else errors
    try:
        with opener(args.path, 'rb') as stream:
            summary = analyze_events(read_jsonl(stream, max_events=args.max_events,
                                                max_line_bytes=args.max_line_bytes),
                                     gap_s=args.gap, max_events=args.max_events)
        report = dict(schema='offline_replay_analytics_v1',
                      flight_validated=False, causal_diagnosis=False,
                      battery_units='reported_percentage_points',
                      interval_rule='left_endpoint_no_final_extrapolation',
                      summary=asdict(summary))
        text = json.dumps(report, allow_nan=False, sort_keys=True, ensure_ascii=True)
    except (ValueError, OSError, TypeError, OverflowError):
        print('Replay analysis rejected input or could not read it; no report produced.',
              file=errors)
        return 2
    print(text, file=output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
