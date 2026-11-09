"""Bounded deterministic kinematic mission simulation; no flight transport.

Instant velocity changes, perfect tracking and no obstacles are deliberate toy
assumptions. A completed trajectory means only that the interpolation ended.
"""
from dataclasses import dataclass
from bisect import bisect_right
import math

from .mission_schema import Mission, number
from .validation import vector


@dataclass(frozen=True)
class Segment:
    start_time: float
    end_time: float
    start: tuple
    end: tuple
    waypoint: str
    phase: str


@dataclass(frozen=True)
class Sample:
    time: float
    position: tuple
    waypoint: str
    phase: str


@dataclass(frozen=True, init=False)
class Trajectory:
    """Precompute at most two segments per point, not one object per timestep.

    `start` must use the same caller-established local ENU origin as the mission.
    `max_duration` is an offline resource budget in seconds, not an FC timeout.
    All position interpolation is 3D Euclidean constant speed in metres/second.
    """

    mission: Mission
    start: tuple
    max_duration: float
    segments: tuple
    end_times: tuple
    duration: float
    distance: float
    dwell: float

    def __init__(self, mission, start=(0.0, 0.0, 0.0), max_duration=3600.0):
        if type(mission) is not Mission:
            raise ValueError('validated Mission required')
        number(max_duration, 'max_duration', 0.001, 86400.0)
        if (not vector(start, 3) or math.hypot(start[0], start[1]) >= mission.radius
                or not 0 <= start[2] < mission.ceiling):
            raise ValueError('start must be finite and strictly inside mission fence')
        object.__setattr__(self, 'mission', mission)
        object.__setattr__(self, 'start', tuple(float(x) for x in start))
        object.__setattr__(self, 'max_duration', float(max_duration))
        segments = []
        previous = self.start
        elapsed = 0.0
        distances = []
        dwells = []
        for point in mission.waypoints:
            destination = point.position
            distance = math.dist(previous, destination)
            distances.append(distance)
            travel_time = distance / mission.speed
            if distance > 0:
                end = math.fsum((elapsed, travel_time))
                if end <= elapsed:
                    raise ValueError('travel interval below floating-point time resolution')
                segments.append(Segment(elapsed, end, previous, destination,
                                        point.name, 'travel'))
                elapsed = end
            if point.dwell > 0:
                end = math.fsum((elapsed, point.dwell))
                if end <= elapsed:
                    raise ValueError('dwell interval below floating-point time resolution')
                segments.append(Segment(elapsed, end, destination, destination,
                                        point.name, 'dwell'))
                elapsed = end
            dwells.append(point.dwell)
            previous = destination
            if elapsed > max_duration:
                raise ValueError('mission exceeds offline duration budget')
        object.__setattr__(self, 'segments', tuple(segments))
        object.__setattr__(self, 'end_times', tuple(segment.end_time for segment in segments))
        object.__setattr__(self, 'duration', elapsed)
        object.__setattr__(self, 'distance', math.fsum(distances))
        object.__setattr__(self, 'dwell', math.fsum(dwells))

    def at(self, elapsed):
        """Query at nonnegative seconds; times at/after completion return final point."""
        number(elapsed, 'elapsed', 0, 1e9)
        if elapsed >= self.duration:
            final = self.mission.waypoints[-1]
            return Sample(float(elapsed), final.position, final.name, 'complete')
        segment = self.segments[bisect_right(self.end_times, elapsed)]
        fraction = (elapsed - segment.start_time) / (segment.end_time - segment.start_time)
        position = tuple(a + (b - a) * fraction
                         for a, b in zip(segment.start, segment.end))
        return Sample(float(elapsed), position, segment.waypoint, segment.phase)

    def samples(self, interval=0.1, max_samples=10000):
        """Return a bounded tuple including t=0 and exact completion once.

        The budget uses ceil(duration/interval)+1 before allocating any samples;
        it is deliberately conservative at floating-point grid boundaries.
        """
        number(interval, 'interval', 0.001, 3600)
        if type(max_samples) is not int or not 1 <= max_samples <= 100000:
            raise ValueError('max_samples must be integer in [1, 100000]')
        steps = math.ceil(self.duration / interval)
        if steps + 1 > max_samples:
            raise ValueError('sample count exceeds offline budget')
        result = []
        for index in range(steps + 1):
            elapsed = min(index * interval, self.duration)
            if not result or elapsed > result[-1].time:
                result.append(self.at(elapsed))
        return tuple(result)

    def summary(self):
        """Fresh machine-readable metrics; explicitly identifies nonphysical model."""
        return {'model': 'offline_constant_speed_enu_v1',
                'flight_validated': False, 'obstacles_modelled': False,
                'duration_s': self.duration, 'distance_m': self.distance,
                'dwell_s': self.dwell, 'waypoints': len(self.mission.waypoints),
                'segments': len(self.segments)}
