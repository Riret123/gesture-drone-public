# Offline multi-agent separation example

Use installed Python modules or the source environment used by the test runner:

```python
from gesture_control.mission_binding import bind
from gesture_control.mission_schema import Mission, Waypoint
from gesture_control.swarm_separation import AgentPlan, assess_fleet

eastbound = Mission((Waypoint('east', 1, 0, 1),), speed=1)
northbound = Mission((Waypoint('north', 0, 1, 1),), speed=1)
a = AgentPlan('a', bind(eastbound, 'toy_lab_enu', 1), start=(-1, 0, 1))
b = AgentPlan('b', bind(northbound, 'toy_lab_enu', 1), start=(0, -1, 1))
report = assess_fleet((a, b), horizon=2, minimum_separation=.5)
assert report['conflict'] is True
assert report['flight_validated'] is False
```

The ideal paths intersect around t=1 second. Looking only at t=0 and t=2 would
miss it. Computed distance/time may differ from exact mathematical values by
floating-point rounding; tests use independent expected geometric values with
tolerance. The production inclusive threshold comparison is not epsilon-expanded.

The origin is only a caller-established label. This example supplies no actual
home measurement, tag calibration or localization. Agent start points are copied
to immutable tuples and validated against each plan's offline fence. Delays and
path intervals that vanish under global floating-point time resolution refuse.

Report includes every pair's IDs, minimum time/distance and conflict flag, plus
origin/revision, finite horizon and caller threshold. It contains no arm, mode,
setpoint, MAVLink or ROS output. Missing fleet members are not detected: supplying
only two plans says nothing about a third vehicle. No real-world separation or
collision-avoidance claim is made.

Resource limits are explicit: at most 32 agents, 256 points per mission and two
segments per point. Trajectory queries use binary search over immutable end times.
This is a reviewable simulation/portfolio experiment; physical swarm operations
remain outside project authorization.
