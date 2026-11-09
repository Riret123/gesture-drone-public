"""Opt-in fixture classifier; existing flight gesture classifier is unchanged."""
import math
from .validation import vector


def classify(points) -> str:
    """21 (x,y) normalized points, image y down. Heuristic, not camera validated."""
    if (not isinstance(points, (tuple, list)) or len(points) != 21
            or not all(vector(p, 2) for p in points)):
        return 'other'
    cx = sum(points[i][0] for i in (0, 5, 9, 13, 17)) / 5
    cy = sum(points[i][1] for i in (0, 5, 9, 13, 17)) / 5
    def radius(i):
        return math.hypot(points[i][0] - cx, points[i][1] - cy)
    extended = [radius(tip) > 1.1 * radius(base)
                for tip, base in ((4, 2), (8, 5), (12, 9), (16, 13), (20, 17))]
    if extended == [True, False, False, False, False]:
        delta = points[4][1] - points[2][1]
        return 'thumbs_up' if delta < -.1 else ('thumbs_down' if delta > .1 else 'other')
    if extended == [False, True, True, False, False]:
        return 'peace'
    if extended == [False, True, False, False, False]:
        return 'pointing'
    if not any(extended):
        return 'fist'
    return 'open_palm' if sum(extended) >= 4 else 'other'
