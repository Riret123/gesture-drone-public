# Round 01: baseline and schema acceptance

## Q01-01: baseline
Before changes `python -B tests/run_all.py` passed 60 unittest methods on Windows.
The root live integration script was not imported or run.

## Q01-02: roundtrip oracle
Parse -> canonical JSON -> parse preserves frozen mission values. Export mutation
does not change an accepted point. These verify data semantics, not flight.

## Q01-03: ambiguity campaign
Duplicate keys at top-level and nested level are errors. Version bool/float/string
and alternate frames are errors. Unknown fields cannot silently alter intent.

## Q01-04: numeric campaign
Every point numeric field is challenged with bool, text, None, NaN, infinity and
an overflowing integer. Tests require ValueError rather than leaked TypeError.

## Q01-05: geometry campaign
East boundary, negative north boundary, ceiling and negative altitude rejected.
Interior path safety is only geometric; no obstacle or localization claim tested.

## Q01-06: resource campaign
Empty arrays, nonarrays, 257 rows, oversized text, malformed surrogate and deep
JSON are rejected. Maximum valid plan remains a follow-up boundary test.

## Q01-07: direct-call campaign
Mission constructor rejects malformed list, boolean version/speed and boundary
points. Immutable dataclass validation protects non-JSON callers as well.

## Q01-08: evidence limit
No SITL, ROS, physical board, real route, terrain or collision tests performed.
Parser test success means only contract acceptance/rejection on synthetic data.

## Q01-09: next campaign
Add seeded valid-plan generation, deterministic simulator invariants, maximum
valid input boundaries, and mission-wide time budgets before CLI exposure.
