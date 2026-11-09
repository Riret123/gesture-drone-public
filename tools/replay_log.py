"""Print validated local logs; never publish replayed flight commands."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.recording import replay

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    parser.add_argument('--format', choices=('csv', 'jsonl'), default='jsonl')
    args = parser.parse_args()
    with open(args.path, encoding='utf-8', newline='') as source:
        for event in replay(source, args.format):
            print(event)
