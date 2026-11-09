"""Read-only validation of the restricted core ROS YAML schema."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/drone_bringup'))
from drone_bringup.core_configuration import parse_core_yaml


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path, default=ROOT / 'config/core.yaml')
    args = parser.parse_args(argv)
    try:
        with args.path.open(encoding='utf-8') as stream:
            parse_core_yaml(stream.read(16385))
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 2
    print('PASS: core YAML schema and reviewed bounds; no hardware checks performed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
