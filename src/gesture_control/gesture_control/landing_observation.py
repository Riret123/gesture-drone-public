"""Strict offline tag observations. No detector, transport or flight output.

Coordinates are camera optical axes (right, down, forward), metres. Times are
local monotonic receive times: a remote detector timestamp is not interchangeable.
Limits are supplied by an experiment owner; none are flight-qualified defaults.
"""
from dataclasses import dataclass
from .validation import finite, vector


@dataclass(frozen=True)
class ObservationLimits:
    max_age_s: float
    max_reprojection_px: float
    max_position_sigma_m: float
    min_depth_m: float
    max_depth_m: float

    def __post_init__(self):
        values = (self.max_age_s, self.max_reprojection_px,
                  self.max_position_sigma_m, self.min_depth_m, self.max_depth_m)
        if not all(finite(v) and v > 0 for v in values):
            raise ValueError('positive finite experiment limits required')
        if self.min_depth_m >= self.max_depth_m:
            raise ValueError('depth interval must increase')


@dataclass(frozen=True)
class TagObservation:
    tag_id: int
    camera_id: str
    calibration_id: str
    received_s: float
    position_m: tuple
    reprojection_px: float
    position_sigma_m: float


@dataclass(frozen=True)
class ObservationDecision:
    accepted: bool
    reason: str
    position_m: tuple | None = None


class ObservationGate:
    """Reject malformed, stale, ambiguous-source or uncalibrated observations.

    Acceptance means only this metadata contract passed. A plausible false tag or
    wrong-but-matching calibration cannot be detected from this contract.
    """
    def __init__(self, tag_id: int, camera_id: str, calibration_id: str,
                 limits: ObservationLimits):
        if type(tag_id) is not int or tag_id < 0:
            raise ValueError('nonnegative integer tag ID required')
        if not all(type(v) is str and v.strip() == v and v
                   for v in (camera_id, calibration_id)):
            raise ValueError('nonempty exact camera/calibration IDs required')
        if not isinstance(limits, ObservationLimits):
            raise ValueError('validated limits required')
        self.tag_id = tag_id
        self.camera_id = camera_id
        self.calibration_id = calibration_id
        self.limits = limits

    def evaluate(self, observation: TagObservation | None,
                 now_s: float) -> ObservationDecision:
        reject = lambda reason: ObservationDecision(False, reason)
        if not finite(now_s) or now_s < 0:
            return reject('invalid_clock')
        if not isinstance(observation, TagObservation):
            return reject('missing_observation')
        o = observation
        if type(o.tag_id) is not int or o.tag_id != self.tag_id:
            return reject('wrong_tag')
        if o.camera_id != self.camera_id or type(o.camera_id) is not str:
            return reject('wrong_camera')
        if o.calibration_id != self.calibration_id or type(o.calibration_id) is not str:
            return reject('wrong_calibration')
        if not finite(o.received_s) or o.received_s < 0 or o.received_s > now_s:
            return reject('invalid_receive_time')
        if now_s - o.received_s > self.limits.max_age_s:
            return reject('stale')
        if not vector(o.position_m, 3):
            return reject('invalid_position')
        if not self.limits.min_depth_m <= o.position_m[2] <= self.limits.max_depth_m:
            return reject('depth_outside_experiment')
        if not finite(o.reprojection_px) or o.reprojection_px < 0:
            return reject('invalid_reprojection')
        if o.reprojection_px > self.limits.max_reprojection_px:
            return reject('reprojection_too_high')
        if not finite(o.position_sigma_m) or o.position_sigma_m < 0:
            return reject('invalid_uncertainty')
        if o.position_sigma_m > self.limits.max_position_sigma_m:
            return reject('uncertainty_too_high')
        return ObservationDecision(True, 'metadata_valid', tuple(o.position_m))
