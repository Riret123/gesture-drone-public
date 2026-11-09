# R01 V06 - acceptance evidence
Executable tests: `tests/test_landing_observation.py` covers explicit limit validation, exact identity, boolean rejection, malformed/nonfinite position, quality bounds, future and invalid clocks, stale boundary, depth limits, missing observations and immutable output.

Review: gate returns reason codes, no control actions or ROS imports. The input dataclass intentionally permits construction of invalid fields so the trust boundary is exercised by the gate rather than silently coercing values. Existing live gesture thresholds, takeoff altitude, modes and bridge behavior are unchanged.

Open: detector implementation, true capture timestamps, replay order, quality-estimate calibration, multi-tag ambiguity, physical calibration, moving-target uncertainty. Unit tests cannot close these items.
