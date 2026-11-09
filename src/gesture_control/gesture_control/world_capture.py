"""Bounded camera-only world-landmark collection through injected adapters."""
from dataclasses import dataclass
from .pose_features import _angles
from .validation import finite


@dataclass(frozen=True)
class WorldFrame:
    time: float
    points: tuple


def collect_world(cap, hands, convert, clock, *, target=30, timeout=30., budget_ms=200.):
    """No ROS/commands/images retained. Native calls are not interrupted here."""
    if (type(target) is not int or not 5 <= target <= 900
            or not finite(timeout) or not 1 <= timeout <= 300
            or not finite(budget_ms) or not 20 <= budget_ms <= 500):
        raise ValueError('require 5..900 frames, timeout 1..300 s, frame budget 20..500 ms')
    started = previous = clock()
    if not finite(started) or started < 0:
        raise ValueError('invalid capture clock')
    frames, seen = [], set()
    attempts = 0
    for _ in range(target * 20):
        before = clock()
        if not finite(before) or before < previous:
            raise ValueError('capture clock reversed or invalid')
        if before - started >= timeout:
            break
        attempts += 1
        ok, image = cap.read()
        points = None
        if ok:
            result = hands.process(convert(image))
            worlds = result.multi_hand_world_landmarks or []
            images = result.multi_hand_landmarks or []
            if len(worlds) == len(images) == 1:
                try:
                    candidate = tuple((p.x, p.y, p.z) for p in worlds[0].landmark)
                    if _angles(candidate) is not None:
                        points = candidate
                except (AttributeError, TypeError):
                    points = None
        after = clock()
        if not finite(after) or after < before:
            raise ValueError('capture clock reversed or invalid')
        previous = after
        stamp = after - started
        if stamp >= timeout:
            break
        if (points is not None and points not in seen
                and (after-before)*1000 <= budget_ms
                and (not frames or stamp > frames[-1].time)):
            frames.append(WorldFrame(stamp, points))
            seen.add(points)
            if len(frames) == target:
                break
    return tuple(frames), {'attempts': attempts, 'accepted': len(frames),
                           'complete': len(frames) == target,
                           'timestamp': 'inference completion relative to start; not exposure'}
