"""Camera-only world CSV recorder; no ROS, FC services or image storage."""
import argparse
import csv
import io
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/gesture_control'))
from gesture_control.camera_settings import CameraSettings
from gesture_control.world_capture import collect_world


def output_path(value):
    path = Path(value).expanduser().resolve()
    if path.is_relative_to(ROOT):
        raise ValueError('recordings must be outside the source checkout')
    if path.exists() or not path.parent.is_dir():
        raise ValueError('use a new output file in an existing external directory')
    return path


def _capture(args, settings):
    cap = hands = None
    try:
        import cv2
        import mediapipe as mp
        version = getattr(mp, '__version__', None)
        if not isinstance(version, str) or not version or version == 'unknown':
            raise ValueError('identified MediaPipe version required before capture')
        cap = cv2.VideoCapture(args.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        cap.set(cv2.CAP_PROP_FPS, settings.fps)
        if not settings.matches(cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FPS)):
            raise ValueError('negotiated camera settings mismatch; recording refused')
        hands = mp.solutions.hands.Hands(model_complexity=settings.model_complexity,
                                         min_detection_confidence=.6,
                                         min_tracking_confidence=.5, max_num_hands=2)
        def convert(image):
            result = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            result.flags.writeable = False
            return result
        frames, report = collect_world(cap, hands, convert, time.monotonic,
                                        target=args.frames, timeout=args.timeout)
        return frames, report, version
    finally:
        try:
            if cap is not None:
                cap.release()
        finally:
            if hands is not None:
                hands.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--label', choices=('open_palm', 'fist'), required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--frames', type=int, default=30)
    parser.add_argument('--timeout', type=float, default=30.)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    parser.add_argument('--fps', type=float, default=30.)
    parser.add_argument('--model', type=int, default=0)
    args = parser.parse_args(argv)
    try:
        settings = CameraSettings(args.width, args.height, args.fps, args.model)
        if not 0 <= args.camera <= 32 or not 5 <= args.frames <= 900 or not 1 <= args.timeout <= 300:
            raise ValueError('camera/frame/timeout outside reviewed bounds')
        destination = output_path(args.output)
    except ValueError as exc:
        parser.error(str(exc))
    if not args.capture:
        print(json.dumps({'execution': 'none; add --capture only with bridge stopped and exclusive camera',
                          'label': args.label, 'frames': args.frames,
                          'images_saved': False, 'flight_commands': False}))
        return 0
    try:
        frames, report, version = _capture(args, settings)
        if not report['complete']:
            raise ValueError('not enough distinct valid one-hand frames; no output saved')
        text = io.StringIO(newline='')
        writer = csv.writer(text, lineterminator='\n')
        writer.writerow(('time', 'hand', 'index', 'x', 'y', 'z'))
        for frame in frames:
            for index, point in enumerate(frame.points):
                writer.writerow((f'{frame.time:.9f}', 0, index, *(f'{v:.9f}' for v in point)))
        with destination.open('x', encoding='utf-8', newline='') as stream:
            stream.write(text.getvalue())
        report.update(label=args.label,
                      camera_id=f'camera-{args.camera}-{settings.width}x{settings.height}-{settings.fps:g}fps-mirror1',
                      model_id=f'mediapipe:{version}:hands-world:model{settings.model_complexity}')
        print(json.dumps(report))
        return 0
    except (Exception, KeyboardInterrupt):
        print('Capture refused/failed; inspect camera/model/ownership and discard any partial output', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
