"""Landmark-only CSV dataset tools; no images, camera or personal metadata."""
import csv
import math
from .extended_gestures import classify

LABELS = ('fist', 'open_palm', 'thumbs_up', 'thumbs_down', 'peace', 'pointing', 'other')
HEADER = ['label'] + [f'{axis}{i}' for i in range(21) for axis in ('x', 'y')]


def record(stream, samples) -> int:
    writer = csv.writer(stream)
    writer.writerow(HEADER)
    count = 0
    for label, points in samples:
        if label not in LABELS or len(points) != 21 or any(len(p) != 2 for p in points):
            raise ValueError('invalid sample shape/label')
        values = [v for p in points for v in p]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('nonfinite landmark')
        writer.writerow([label, *values])
        count += 1
    return count


def evaluate(stream) -> dict:
    rows = csv.reader(stream)
    if next(rows, None) != HEADER:
        raise ValueError('invalid CSV header')
    matrix = {label: {guess: 0 for guess in LABELS} for label in LABELS}
    total = correct = 0
    for row in rows:
        if len(row) != 43 or row[0] not in LABELS:
            raise ValueError('invalid CSV row')
        values = [float(v) for v in row[1:]]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('nonfinite landmark')
        guess = classify(list(zip(values[::2], values[1::2])))
        matrix[row[0]][guess] += 1
        total += 1
        correct += guess == row[0]
    return dict(total=total, accuracy=correct / total if total else None, confusion=matrix)
