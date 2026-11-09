"""Evaluate landmark CSV without loading a camera; stdout JSON confusion matrix."""
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.dataset import evaluate

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv')
    args = parser.parse_args()
    with open(args.csv, encoding='utf-8', newline='') as stream:
        print(json.dumps(evaluate(stream), indent=2))
