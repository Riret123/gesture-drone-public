# Backend round 02 review

Implemented `mission_simulation.py` and `mission_cli.py`, three checked-in JSON
examples and usage documentation. Extended schema tests and added simulator/CLI
test files. Analytic lookup avoids accumulated timestep integration error; frozen
trajectories prevent ordinary accidental reconfiguration. Positive time intervals
below machine resolution are explicitly rejected.

Round-1 attacks: B-R01-1 fixed by maximal-precision 256-point roundtrip;
B-R01-3 has bounded/deep JSON rejection coverage; B-R01-4 fixed by all plan-number
type mutations; B-R01-5 fixed by exact export-key tests. B-R01-2 remains open:
error messages are categories, no structured UI field-path contract yet. CLI
intentionally suppresses raw payload/path details in failure output.

Proposed offline behavior is explicit: 0.2 m/s input default, 20 m radius and 5 m
ceiling inherited from the new mission schema only; no live flight setting is
changed. Toy duration/sample limits are described in ADR 002.

Next: origin-bound mission plans, continuous pairwise swarm separation prediction,
and a ROS-shaped in-memory harness with no middleware imports or send transport.
