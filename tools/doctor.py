"""Read-only board doctor; camera capture requires --probe-camera."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/drone_bringup'))
from drone_bringup.doctor import COMMANDS, diagnose


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT)
    parser.add_argument('--probe-camera', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args(argv)
    if args.plan:
        print(json.dumps({'read_only_probes': COMMANDS,
                          'camera_probe_requested': args.probe_camera}, indent=2))
        return 0
    results = diagnose(args.workspace, probe_camera=args.probe_camera)
    print(json.dumps(results, indent=2))
    return 2 if any(item['status'] == 'fail' for item in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
