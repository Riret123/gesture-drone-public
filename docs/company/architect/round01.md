# Round 01: mission contract foundation

## A01-01: trust boundary
Mission JSON is untrusted data. The parser opens no files, executes no strings,
imports no ROS, and returns an immutable value. No data field names a publisher.

## A01-02: coordinate contract
Version 1 accepts only `local_enu`: east, north, up in metres from an explicitly
defined future home. WGS84, NED, and unnamed frames are rejected, not converted.
An adapter must establish surveyed/calibrated home independently before use.

## A01-03: waypoint identity
Names use ASCII letter then letters/digits/underscore/hyphen, at most 32 chars.
Names must be unique. Names are labels, not filesystem paths or HTML fragments.

## A01-04: constructor parity
Frozen Waypoint and Mission constructors validate directly; callers cannot
bypass JSON checks by creating a list or malformed object programmatically.
Exported dictionaries are fresh snapshots and do not mutate the mission.

## A01-05: bounded ingestion
The parser caps UTF-8 at 65,536 bytes and 256 waypoints. Dwell is bounded to
3,600 seconds per point; coordinates are bounded before distance calculations.
These are parser resource limits, not an operational envelope.

## A01-06: duplicate-key policy
Duplicate JSON keys are rejected at every object depth. No last-key-wins policy
is allowed for safety-relevant configuration. Nonstandard NaN/Infinity rejected.

## A01-07: fence semantics
A circular local fence has strictly excluded lateral and upper boundaries.
Ground height zero is accepted. Straight segments between interior endpoints
remain inside this convex fence; this says nothing about terrain or obstacles.

## A01-08: version migration decision
Only integer version 1 accepted. Unknown keys rejected. A future schema version
needs an explicit migration function and fixtures; silent fallback is forbidden.
Canonical JSON sorts keys and forbids nonfinite numbers for stable review diffs.

## A01-09: integration gate
No live importer added. Simulator and mission CLI will consume this value in
later rounds. ROS mapping, trajectory dynamics, home acquisition and FC-level
failsafes remain blocked pending independent design and SITL validation.
