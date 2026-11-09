"""Experimental 3D joint angles; explicit saved profiles can select the live path.

Requires consistent metric coordinates (e.g. world landmarks); mixing image x/y
with model z is not a measured Euclidean geometry. Confidence is a margin score,
not a probability. Synthetic invariance cannot establish camera accuracy.
"""
from dataclasses import dataclass
import math
from .validation import finite, vector


@dataclass(frozen=True)
class PoseProfile:
    folded_max: float = 110.0
    extended_min: float = 160.0
    min_confidence: float = .5

    def __post_init__(self):
        if (not all(finite(v) for v in (self.folded_max, self.extended_min,
                                        self.min_confidence))
                or not 0 < self.folded_max < self.extended_min < 180
                or not 0 <= self.min_confidence <= 1):
            raise ValueError('require separated finite angles and confidence in [0,1]')


@dataclass(frozen=True)
class PoseResult:
    gesture: str
    confidence: float
    reason: str


def _angles(points):
    if (not isinstance(points, (tuple, list)) or len(points) != 21
            or not all(vector(p, 3) and all(abs(v) <= 1e6 for v in p)
                       for p in points)):
        return None
    angles = []
    for base in (5, 9, 13, 17):
        for joint in (base + 1, base + 2):
            a = tuple(points[joint - 1][i] - points[joint][i] for i in range(3))
            b = tuple(points[joint + 1][i] - points[joint][i] for i in range(3))
            na, nb = math.hypot(*a), math.hypot(*b)
            if min(na, nb) <= 1e-9:
                return None
            cosine = sum((x / na) * (y / nb) for x, y in zip(a, b))
            angles.append(math.degrees(math.acos(max(-1., min(1., cosine)))))
    # Reject palms that cannot define a plane; side-on projection alone is not
    # degenerate in true 3D, while collapsed or collinear model output is.
    a = tuple(points[5][i] - points[0][i] for i in range(3))
    b = tuple(points[17][i] - points[0][i] for i in range(3))
    cross = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    if math.hypot(*cross) <= 1e-9:
        return None
    return angles


def classify_pose(points, profile):
    if not isinstance(profile, PoseProfile):
        raise ValueError('profile must be a validated PoseProfile')
    angles = _angles(points)
    if angles is None:
        return PoseResult('other', 0., 'invalid_geometry')
    if min(angles) >= profile.extended_min:
        confidence = min(1., (min(angles)-profile.extended_min)
                         / (180-profile.extended_min))
        gesture = 'open_palm'
    elif max(angles) <= profile.folded_max:
        confidence = min(1., (profile.folded_max-max(angles)) / 20.)
        gesture = 'fist'
    else:
        return PoseResult('other', 0., 'ambiguous_angles')
    if confidence < profile.min_confidence:
        return PoseResult('other', confidence, 'low_margin')
    return PoseResult(gesture, confidence, 'accepted')


def calibrate(open_samples, fist_samples):
    """Conservative training envelopes only; held-out user sessions still required."""
    groups = []
    for samples in (open_samples, fist_samples):
        if not isinstance(samples, (list, tuple)) or not 5 <= len(samples) <= 1000:
            raise ValueError('require 5..1000 labeled samples per gesture')
        group = [_angles(points) for points in samples]
        if any(angles is None for angles in group):
            raise ValueError('calibration contains invalid geometry')
        groups.append(group)
    opened_min = min(min(angles) for angles in groups[0])
    folded_max = max(max(angles) for angles in groups[1])
    if opened_min - folded_max < 30:
        raise ValueError('calibration classes overlap or lack a 30 degree margin')
    return PoseProfile(folded_max=min(150., folded_max + 10),
                       extended_min=min(175., opened_min - 10))
