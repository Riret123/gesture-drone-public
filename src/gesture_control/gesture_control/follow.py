"""Offline bounding-box following proposals with conditional PID integration."""
import math


class PID:
    def __init__(self, kp: float = .4, ki: float = .1, kd: float = .02,
                 limit: float = .2):
        if not all(math.isfinite(v) for v in (kp, ki, kd, limit)) or limit <= 0:
            raise ValueError('invalid PID configuration')
        self.kp, self.ki, self.kd, self.limit = kp, ki, kd, limit
        self.integral = 0.
        self.previous = None

    def reset(self) -> None:
        self.integral, self.previous = 0., None

    def update(self, error: float, dt: float) -> float:
        if not math.isfinite(error) or not math.isfinite(dt) or dt <= 0:
            raise ValueError('finite error and positive dt required')
        derivative = 0 if self.previous is None else (error - self.previous) / dt
        candidate = self.integral + error * dt
        raw = self.kp * error + self.ki * candidate + self.kd * derivative
        if abs(raw) <= self.limit or raw * error < 0:
            self.integral = candidate
        self.previous = error
        return max(-self.limit, min(self.limit, raw))


class FollowController:
    """Box (left,top,right,bottom) in [0,1]; area target 0.2; no identity tracker."""

    def __init__(self):
        self.center = PID()
        self.size = PID()

    def update(self, box: tuple | None, dt: float) -> tuple[float, float]:
        if box is None:
            self.center.reset()
            self.size.reset()
            return 0., 0.
        if (len(box) != 4 or not all(math.isfinite(v) and 0 <= v <= 1 for v in box)
                or box[0] >= box[2] or box[1] >= box[3]):
            return self.update(None, dt)
        left, top, right, bottom = box
        return (self.center.update((left + right) / 2 - .5, dt),
                self.size.update(.2 - (right - left) * (bottom - top), dt))
