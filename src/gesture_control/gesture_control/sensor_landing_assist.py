"""Offline planar flow/range estimate. Never a descent or control command."""
from dataclasses import dataclass
import math
from .validation import finite, vector


@dataclass(frozen=True)
class RangeFlowSample:
    received_s: float
    slant_range_m: float
    tilt_rad: float
    angular_flow_xy_rps: tuple
    quality: float
    rotation_compensated: bool
    planar_surface_assumed: bool


@dataclass(frozen=True)
class AssistEstimate:
    status: str
    reason: str
    height_m: float | None = None
    speed_xy_mps: tuple | None = None


def estimate_planar_flow(sample, now_s: float, *, max_age_s: float,
                         min_range_m: float, max_range_m: float,
                         max_tilt_rad: float, min_quality: float,
                         max_angular_flow_rps: float) -> AssistEstimate:
    """Small-angle planar estimate height=r*cos(tilt), speed=height*flow.

    Flow axes/signs are caller-defined camera-plane quantities, not body velocity.
    Rotation compensation and planar-surface flags are attestations, not measured
    facts. Lidar validity, reflectivity and multiple returns are adapter concerns.
    """
    if (not all(finite(v) and v > 0 for v in
                (max_age_s, min_range_m, max_range_m, max_tilt_rad,
                 min_quality, max_angular_flow_rps))
            or min_range_m >= max_range_m or max_tilt_rad >= math.pi / 2
            or min_quality > 1):
        raise ValueError('explicit finite valid offline assist limits required')
    reject = lambda reason: AssistEstimate('UNAVAILABLE', reason)
    if not finite(now_s) or now_s < 0:
        return reject('invalid_clock')
    if not isinstance(sample, RangeFlowSample):
        return reject('missing_sample')
    s = sample
    if not finite(s.received_s) or s.received_s < 0 or s.received_s > now_s:
        return reject('invalid_receive_time')
    if now_s - s.received_s > max_age_s:
        return reject('stale')
    if (type(s.rotation_compensated) is not bool or not s.rotation_compensated
            or type(s.planar_surface_assumed) is not bool or not s.planar_surface_assumed):
        return reject('model_preconditions_missing')
    if not finite(s.slant_range_m) or not min_range_m <= s.slant_range_m <= max_range_m:
        return reject('range_outside_experiment')
    if not finite(s.tilt_rad) or abs(s.tilt_rad) > max_tilt_rad:
        return reject('tilt_outside_experiment')
    if not finite(s.quality) or not min_quality <= s.quality <= 1:
        return reject('quality_too_low_or_invalid')
    if not vector(s.angular_flow_xy_rps, 2):
        return reject('invalid_flow')
    if math.hypot(*s.angular_flow_xy_rps) > max_angular_flow_rps:
        return reject('flow_outside_experiment')
    height = s.slant_range_m * math.cos(s.tilt_rad)
    speed = tuple(height * flow for flow in s.angular_flow_xy_rps)
    if not all(math.isfinite(v) for v in (height, *speed)):
        return reject('arithmetic_overflow')
    return AssistEstimate('MODEL_ESTIMATE', 'unverified_planar_model', height, speed)
