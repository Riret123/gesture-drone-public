# Round 04: legacy offline control input audit

Ten new regression methods initially produced seven failures and three unexpected
exceptions. Narrow fixes modify only offline helpers, not ROS wrappers.

Disclosed behavior changes:

- Deadman: bool/overflow/nonfinite configuration and clocks reject; invalid clock
  revokes a remembered release; sample timestamps must strictly advance, so a
  repeated release/press at the same timestamp cannot re-enable. Invalid data
  still returns false, invalid local clock raises ValueError. Timeout remains
  0.25 seconds by default. There is no transport authentication or live input.
- Velocity mapping: malformed limit/deadzone configuration rejects consistently
  as ValueError, including bools and huge integers. Existing 0.2 speed limit,
  0.1 deadzone and disabled-by-default behavior are unchanged.
- Slew: stop requires exact bool; malformed vectors/dt/configuration reject;
  unrepresentable acceleration steps reject rather than divide by zero. Stable
  normalization preserves large finite target direction instead of mapping it
  to zero. Default acceleration/speed remain 0.3 and 0.2. Invalid updates raise
  before mutating the previous value; this is not an automatic live stop policy.

The prior deadman test used the same sample time for an initial held press and a
subsequent release. Updated that fixture to a distinct .05-second release because
replay rejection intentionally disallows contradictory events at one timestamp.
The new replay regression preserves this requirement separately.

Next review: PID/filter arithmetic can create NaN from finite extreme inputs;
all derived state must be validated before mutation. No live gain or gesture
threshold changes are authorized by this review.
