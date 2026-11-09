"""Offline differential-drive rover policy; SI units; no motor I/O."""
import math


def wheels(linear: float, angular: float, track: float = .3,
           limit: float = .4) -> tuple[float, float]:
    """Scale both wheel speeds together to preserve curvature."""
    if not all(math.isfinite(v) for v in (linear, angular, track, limit)):
        raise ValueError('finite inputs required')
    if track <= 0 or limit <= 0:
        raise ValueError('positive geometry and limit required')
    left, right = linear - angular * track / 2, linear + angular * track / 2
    scale = max(1, abs(left) / limit, abs(right) / limit)
    return left / scale, right / scale


def control(mode: str, target: tuple[float, float], age: float,
            timeout: float = .5) -> tuple[float, float]:
    """Target is distance m / heading error rad to person or home.

    Invalid or stale link stops; hold always stops. Follow keeps 1 m separation.
    This is no obstacle avoidance or localization implementation.
    """
    distance, heading = target
    if (not all(math.isfinite(v) for v in (distance, heading, age, timeout))
            or age < 0 or timeout <= 0 or age >= timeout or distance < 0):
        return 0., 0.
    if mode not in ('follow', 'return_home'):
        return 0., 0.
    error = max(0, distance - (1 if mode == 'follow' else 0))
    if error < .05:
        return 0., 0.
    return wheels(min(.2, error * .3) * max(0, math.cos(heading)),
                  max(-1, min(1, heading)))
