"""Offline landing proposal in camera axes: x right, y down, z forward (m).

For a downward camera z approximates height. vx/vy are camera-plane corrections;
vz is positive descent speed, NOT a MAVROS setpoint. Extrinsic calibration and
body/world conversion are required before integration. Contact is external truth.
"""
from dataclasses import dataclass
import math
from .validation import vector


@dataclass(frozen=True)
class LandingCommand:
    state: str
    vx: float = 0.0
    vy: float = 0.0
    descent: float = 0.0


class LandingController:
    """Search without descent; abort on lost pose after acquisition; terminal latch.

    Prototype limits: lateral 0.2 m/s, alignment 0.08 m, final below 0.25 m;
    descent 0.15 m/s or 0.04 m/s final. No automatic disarm or search movement.
    """

    def __init__(self):
        self.state = 'search'

    def update(self, pose: tuple | None, contact: bool = False,
               abort: bool = False) -> LandingCommand:
        if self.state in ('abort', 'touchdown'):
            return LandingCommand(self.state)
        if type(contact) is not bool or type(abort) is not bool:
            self.state = 'abort'
            return LandingCommand(self.state)
        if abort:
            self.state = 'abort'
            return LandingCommand(self.state)
        if pose is None:
            if self.state != 'search':
                self.state = 'abort'
            return LandingCommand(self.state)
        if not vector(pose, 3) or pose[2] <= 0:
            self.state = 'abort'
            return LandingCommand(self.state)
        x, y, z = pose
        error = math.hypot(x, y)
        if contact:
            self.state = 'touchdown' if z <= 0.25 and error <= 0.08 else 'abort'
            return LandingCommand(self.state)
        self.state = 'align' if error > 0.08 else ('final' if z <= 0.25 else 'descend')
        descent = 0 if self.state == 'align' else (0.04 if z <= 0.25 else 0.15)
        scale = min(1.0, 0.2 / max(error, 1e-12))
        return LandingCommand(self.state, x * scale, y * scale, descent)
