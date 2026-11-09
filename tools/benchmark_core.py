"""Measure pure-Python fixture classification only; no camera/MediaPipe/ROS/FC."""
import argparse
import json
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src/gesture_control'), str(ROOT / 'src/drone_bringup')]
from drone_bringup.deterministic_replay import read_landmark_csv
from gesture_control.core_latency import LatencyLedger
from gesture_control.frame_classifier import classify_frame


def measure(frames, repeats):
    if type(repeats) is not int or not 1 <= repeats <= 10000 or not frames:
        raise ValueError('require nonempty fixture and 1..10000 repeats')
    prepared = [[[SimpleNamespace(x=x, y=y, z=z) for x, y, z in hand]
                 for hand in frame.hands] for frame in frames]
    ledger = LatencyLedger(max_samples=10000, budget_ms=100.)
    last = None
    for _ in range(repeats):
        for hands in prepared:
            start = time.perf_counter()
            feature_start = time.perf_counter()
            classify_frame(hands)
            feature_end = time.perf_counter()
            dispatch = time.perf_counter()
            last = (start, feature_start, feature_end, dispatch)
            if not ledger.record(*last):
                raise RuntimeError('invalid measurement clock')
    return {'scope': 'fixture classification; excludes camera, MediaPipe, debounce, ROS and FC',
            'platform': platform.system(), 'architecture': platform.machine(),
            'summary': ledger.summary(), 'last_measured_timestamps': last}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path,
                        default=ROOT / 'tests/fixtures/core_landmarks_synthetic.csv')
    parser.add_argument('--repeats', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        with args.fixture.open(encoding='utf-8') as stream:
            frames = read_landmark_csv(stream.read(2_000_001))
        result = measure(frames, args.repeats)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
