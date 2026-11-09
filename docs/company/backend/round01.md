# Round 01: mission schema implementation

## B01-01: validated point value
`mission_schema.Waypoint` rejects invalid names, boolean numeric values,
nonfinite coordinates, negative altitude/dwell and values outside parser bounds.

## B01-02: validated plan value
`Mission` enforces a nonempty tuple of real Waypoint values, unique names,
speed in [0.01, 2] m/s and a positive bounded offline cylindrical envelope.
The speed range is a toy input domain, not a recommended aircraft speed.

## B01-03: strict dictionary adapter
`from_dict` rejects missing/extra fields in plan and each point. Points must be
a JSON-array-shaped list; no truthy coercions, implicit frame or default version.

## B01-04: strict JSON adapter
`from_json` accepts text only, checks character and UTF-8 size, rejects duplicate
fields and constants, and normalizes malformed JSON/depth/Unicode failures to
ValueError. Future byte-stream callers must decode explicitly before parsing.

## B01-05: immutable snapshot export
`to_dict` builds fresh point dictionaries. A UI may edit its copy without changing
an accepted plan. `to_json` is deterministic and emits standards-compatible JSON.

## B01-06: inspectable positions
`Waypoint.position` returns an ENU tuple with no transform ambiguity. This small
interface prevents simulator code from accidentally treating a label as a vector.

## B01-07: error discipline
Validation errors contain field categories rather than full mission payloads.
Untrusted content is not echoed into logs or interpreted as shell instructions.
Error strings are explanatory, not a stable machine-readable API in version 1.

## B01-08: compatibility boundary
Existing legacy flight behavior, modes, altitude, arming order, timeouts and
gesture thresholds are unchanged. This module has no automatic import into ROS.

## B01-09: next implementation
Build deterministic constant-speed interpolation with finite duration/step caps.
Zero-length legs must still observe dwell. Completion must mean toy path complete,
never a flight acknowledgement or verified touchdown.
