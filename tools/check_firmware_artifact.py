"""Read-only APJ identity/hash check; never downloads or flashes firmware."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/drone_bringup'))
from drone_bringup.firmware_artifact import inspect_apj, MAX_APJ_BYTES


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact', type=Path)
    parser.add_argument('--expected-board-id', type=int, required=True)
    parser.add_argument('--expected-sha256')
    args = parser.parse_args(argv)
    try:
        with args.artifact.open('rb') as stream:
            data = stream.read(MAX_APJ_BYTES + 1)
        report = inspect_apj(data, args.expected_board_id, args.expected_sha256)
    except (OSError, ValueError):
        parser.exit(1, 'Firmware artifact rejected; confirm identity/hash/format locally. Nothing flashed.\n')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
