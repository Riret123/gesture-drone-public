# ADR 002: analytic simulation and explicit resource budgets

Status: accepted, round 02.

Use a piecewise analytic trajectory rather than advancing a mutable simulator
clock. A query at time t is independent of query history. Segment endpoints are
precomputed once; there are at most twice the number of waypoints. Sampling is a
separate bounded operation that allocates only after checking its count budget.

Time is nonnegative elapsed seconds, unrelated to remote timestamps or wall time.
Travel is 3D constant speed; dwell begins exactly at arrival, ends exactly at its
deadline, then the next leg starts. At/after final duration, phase is `complete`.
Zero-length legs preserve dwell. A zero-duration plan yields one complete sample.

Default duration budget is 3,600 seconds; supported override at most 86,400.
Timeline output defaults to at most 10,000 samples; hard cap is 100,000.
Interval domain is [0.001, 3600] seconds. These are CPU/output resource controls,
not airworthiness limits or flight-controller failsafe settings.

Positive segments that disappear under floating-point time resolution are
rejected rather than silently becoming instantaneous. This includes underflow
travel and tiny dwell following a large elapsed time. No arbitrary epsilon is
used to turn invalid geometry into valid data.

Acceptance: duration includes dwell; over-budget count rejected before timeline
allocation; exact final sample appears once; fixed-seed paths are reproducible.
