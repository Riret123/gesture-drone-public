"""Offline origin/revision binding and semantic plan identifiers.

An origin label is caller-established metadata, never proof of surveyed home.
SHA-256 detects plan changes; it is not a signature or sender authentication.
"""
from dataclasses import dataclass
import hashlib
import json
import re

from .mission_schema import Mission


def origin_revision(origin_id, revision):
    if type(origin_id) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,64}', origin_id) is None:
        raise ValueError('bounded ASCII origin identifier required')
    if type(revision) is not int or not 0 <= revision <= 2**31 - 1:
        raise ValueError('nonnegative bounded integer frame revision required')


def semantic_id(mission):
    """Stable digest for this schema, treating equal int/float and signed zero alike.

    Point names, order, dwell, envelope, speed, frame and version are all identity
    inputs. This is a project-local encoding, not an RFC canonical-JSON claim.
    """
    if type(mission) is not Mission:
        raise ValueError('validated Mission required')
    def normalized(value):
        # Convert only known numeric fields; version deliberately stays integer.
        return 0.0 if value == 0 else float(value)
    data = mission.to_dict()
    for name in ('speed', 'radius', 'ceiling'):
        data[name] = normalized(data[name])
    for point in data['waypoints']:
        for name in ('east', 'north', 'up', 'dwell'):
            point[name] = normalized(point[name])
    encoded = json.dumps(data, allow_nan=False, sort_keys=True, separators=(',', ':')).encode('ascii')
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MissionContext:
    origin_id: str
    revision: int
    plan_id: str

    def __post_init__(self):
        origin_revision(self.origin_id, self.revision)
        if type(self.plan_id) is not str or re.fullmatch(r'[0-9a-f]{64}', self.plan_id) is None:
            raise ValueError('lowercase SHA-256 plan identifier required')


@dataclass(frozen=True)
class BoundMission:
    mission: Mission
    context: MissionContext

    def __post_init__(self):
        if type(self.mission) is not Mission or type(self.context) is not MissionContext:
            raise ValueError('validated mission/context required')
        if semantic_id(self.mission) != self.context.plan_id:
            raise ValueError('plan identifier does not match mission')


def bind(mission, origin_id, revision):
    """Bind caller metadata for offline comparisons, without any navigation output."""
    return BoundMission(mission, MissionContext(origin_id, revision, semantic_id(mission)))


def require_context(bound, origin_id, revision):
    """Refuse missing/mismatched binding before a consumer uses plan coordinates."""
    origin_revision(origin_id, revision)
    if type(bound) is not BoundMission:
        raise ValueError('bound mission required')
    if (bound.context.origin_id, bound.context.revision) != (origin_id, revision):
        raise ValueError('mission origin or frame revision mismatch')
    return bound.mission
