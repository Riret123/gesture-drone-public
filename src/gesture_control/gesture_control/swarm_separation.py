"""Continuous pairwise separation for bounded toy ENU trajectories.

No vehicles, middleware, collision avoidance, obstacle model or actuation. A path
has perfect instantaneous tracking; a clearance result is a model observation.
"""
from dataclasses import dataclass, field
import math
import re

from .mission_binding import BoundMission, require_context
from .mission_schema import number
from .mission_simulation import Trajectory


@dataclass(frozen=True)
class AgentPlan:
    agent_id: str
    bound: BoundMission
    start: tuple = (0.0, 0.0, 0.0)
    delay: float = 0.0
    trajectory: Trajectory = field(init=False, repr=False)

    def __post_init__(self):
        if type(self.agent_id) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,32}', self.agent_id) is None:
            raise ValueError('bounded ASCII agent identifier required')
        if type(self.bound) is not BoundMission:
            raise ValueError('origin-bound mission required')
        number(self.delay, 'delay', 0, 86400)
        trajectory = Trajectory(self.bound.mission, start=self.start)
        previous_time = float(self.delay)
        for segment in trajectory.segments:
            global_end = self.delay + segment.end_time
            if global_end <= previous_time:
                raise ValueError('delayed interval below global clock resolution')
            previous_time = global_end
        object.__setattr__(self, 'start', trajectory.start)
        object.__setattr__(self, 'trajectory', trajectory)

    def position_at(self, time):
        number(time, 'time', 0, 86400)
        if time < self.delay:
            return self.trajectory.start
        return self.trajectory.at(time - self.delay).position

    def breakpoints(self, horizon):
        number(horizon, 'horizon', .001, 86400)
        times = {0.0, float(horizon)}
        for elapsed in (0.0,) + tuple(segment.end_time for segment in self.trajectory.segments):
            value = self.delay + elapsed
            if 0 < value < horizon:
                times.add(value)
        return tuple(sorted(times))


@dataclass(frozen=True)
class ClosestApproach:
    first: str
    second: str
    time: float
    distance: float


def closest_approach(first, second, horizon):
    """Analytic piecewise-linear minimum on [0,horizon], to float precision.

    Agents occupy their start before their delay and their final point afterward.
    Matching caller origin/revision is required; labels are not calibration proof.
    """
    number(horizon, 'horizon', .001, 86400)
    if type(first) is not AgentPlan or type(second) is not AgentPlan:
        raise ValueError('validated AgentPlan pair required')
    if first.agent_id == second.agent_id:
        raise ValueError('distinct agent identifiers required')
    require_context(second.bound, first.bound.context.origin_id, first.bound.context.revision)
    boundaries = sorted(set(first.breakpoints(horizon) + second.breakpoints(horizon)))
    best_distance, best_time = math.inf, 0.0
    for begin, end in zip(boundaries, boundaries[1:]):
        a0, b0 = first.position_at(begin), second.position_at(begin)
        a1, b1 = first.position_at(end), second.position_at(end)
        relative = tuple(a - b for a, b in zip(a0, b0))
        change = tuple((a - b) - r for a, b, r in zip(a1, b1, relative))
        magnitude = math.hypot(*change)
        if magnitude == 0:
            fraction = 0.0
        else:
            # Normalize before dot product to avoid squaring subnormal changes.
            direction = tuple(value / magnitude for value in change)
            projection = math.fsum(r * d for r, d in zip(relative, direction))
            fraction = min(1.0, max(0.0, -projection / magnitude))
        distance = math.hypot(*(r + fraction * delta for r, delta in zip(relative, change)))
        time = begin + fraction * (end - begin)
        if distance < best_distance or distance == best_distance and time < best_time:
            best_distance, best_time = distance, time
    return ClosestApproach(first.agent_id, second.agent_id, best_time, best_distance)


def assess_fleet(agents, horizon, minimum_separation):
    """Report all pair minima for 2–32 agents; never produce velocity commands.

    A distance equal to the configured threshold is a conflict. The threshold is
    supplied by the experiment owner, not a flight-qualified safety clearance.
    Missing expected members require a separate registry/heartbeat check.
    """
    number(horizon, 'horizon', .001, 86400)
    number(minimum_separation, 'minimum_separation', .001, 10000)
    if type(agents) not in (tuple, list) or not 2 <= len(agents) <= 32:
        raise ValueError('fleet must contain 2 to 32 AgentPlan values')
    if any(type(agent) is not AgentPlan for agent in agents):
        raise ValueError('validated AgentPlan values required')
    if len({agent.agent_id for agent in agents}) != len(agents):
        raise ValueError('agent identifiers must be unique')
    results = []
    for index, first in enumerate(agents):
        for second in agents[index + 1:]:
            closest = closest_approach(first, second, horizon)
            results.append({'first': closest.first, 'second': closest.second,
                            'time_s': closest.time, 'distance_m': closest.distance,
                            'conflict': closest.distance <= minimum_separation})
    return {'schema': 'offline_swarm_separation_v1', 'flight_validated': False,
            'model': 'perfect_tracking_piecewise_linear_enu',
            'horizon_s': float(horizon), 'minimum_separation_m': float(minimum_separation),
            'origin_id': agents[0].bound.context.origin_id,
            'revision': agents[0].bound.context.revision,
            'conflict': any(row['conflict'] for row in results), 'pairs': results}
