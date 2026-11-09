"""Offline world-landmark calibration. Never opens a camera or sends commands."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src/gesture_control'), str(ROOT / 'src/drone_bringup')]
from drone_bringup.deterministic_replay import read_landmark_csv
from gesture_control.pose_features import calibrate
from gesture_control.pose_profile_io import save_profile


def samples(path):
    with path.open(encoding='utf-8') as stream:
        frames = read_landmark_csv(stream.read(2_000_001))
    if any(len(frame.hands) != 1 for frame in frames):
        raise ValueError('calibration requires exactly one labeled world hand per frame')
    if len({frame.hands[0] for frame in frames}) < 5:
        raise ValueError('require at least five distinct world poses; frozen/repeated frames refused')
    return [list(frame.hands[0]) for frame in frames]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--open', dest='opened', required=True, type=Path)
    parser.add_argument('--fist', required=True, type=Path)
    parser.add_argument('--coordinates', required=True, choices=('world',))
    parser.add_argument('--camera-id', required=True)
    parser.add_argument('--model-id', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--replace-profile', action='store_true')
    args = parser.parse_args(argv)
    try:
        destination = args.output.expanduser().resolve()
        if destination.is_relative_to(ROOT) or not destination.parent.is_dir():
            raise ValueError('profile output requires an existing directory outside source')
        if destination.exists() and not args.replace_profile:
            raise ValueError('existing profile requires explicit --replace-profile')
        profile = calibrate(samples(args.opened.expanduser()), samples(args.fist.expanduser()))
        save_profile(destination, profile, camera_id=args.camera_id, model_id=args.model_id)
    except (OSError, ValueError) as exc:
        print(f'Calibration refused: {exc}', file=sys.stderr)
        return 2
    print('Profile saved; held-out orientation/occlusion validation still required before activation')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
