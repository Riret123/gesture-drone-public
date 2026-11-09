# ADR 004: continuous model separation instead of tick-only checks

Status: accepted as offline model analysis, round 03.

Each AgentPlan occupies its start until a nonnegative delay, follows a validated
trajectory, and occupies its endpoint afterward. Dwell is a stationary segment.
All plans share a caller-established ENU origin/revision and simulation epoch.
Comparisons use a finite closed [0,horizon] interval, at most 86,400 seconds.

For each pair, take the union of both paths' segment endpoints plus delay,
zero and horizon. On each interval the relative path is linear. Project the
origin onto that relative segment, clamp the fraction to [0,1], evaluate its
distance, and keep the smallest pair. Equal computed minima choose earliest time.
Normalize relative displacement before projection to avoid directly squaring
subnormal vectors. Results retain ordinary floating-point error.

Sampling only endpoints can miss two crossing vehicles. This analysis returns
minimum modeled distance/time and never chooses a vehicle priority or command.
The fleet function accepts 2–32 unique agents and reports every pair; distance
equal to the caller-provided minimum separation is a conflict. Threshold domain
is [0.001,10000] metres as a toy input range, not a certified clearance.

No confidence envelope, wind, braking, obstacles, network age, missing-member
registry or physical body shape is modeled. Near-threshold precision and model
uncertainty need a separately reviewed conservative policy before any safety use.
No live controller imports this module. Flight_validated is always false.

Acceptance: between-tick crossing, head-on, parallel, stationary, delayed and
post-completion occupancy; common translation and input swap invariance; analytic
minimum no greater than dense observed minimum within stated numerical tolerance.
