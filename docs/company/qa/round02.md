# QA round 02 review

Added simulator and CLI tests, schema plan-level type mutations, maximum-valid
inputs, UTF-8 bytes, independent geometric oracles and fixed-seed path invariants.
Precision review found silent tiny-interval disappearance; regression tests now
require rejection for underflow travel, unrepresentable dwell and tiny legs after
large dwell. In-memory CLI tests avoid previously documented tempfile restrictions.

Round-1 attacks: Q-R01-1 fixed by largest-valid roundtrip; Q-R01-2 fixed by test
bootstrap and focused invocation in MISSION_CAMPAIGN; Q-R01-3 counting discipline
preserved; Q-R01-4 addressed with independent 3-4-5 oracle and fixed-seed paths.
Q-R01-5 remains blocked: Linux installed-package and colcon validation unavailable.

Full-suite runs after each code sub-batch passed: shared snapshots 115, 138, 155,
157 and 171 methods. Counts include other workers' contemporaneous additions and
must not be summed. Exact final round snapshot is reported separately to root.

Next QA priority: continuous crossing counterexample, origin mismatch, missing
agents, timestamp skew and deterministic mock asynchronous service outcomes.
