# Frontend red team — round 4

| ID | Attack | State | Evidence |
| --- | --- | --- | --- |
| FE25 | enormous deadman clock raises OverflowError | fixed offline | test_deadman_huge_clock_rejected_as_value_error |
| FE26 | invalid clock leaves remembered release active | fixed offline | test_deadman_invalid_clock_revokes_previous_release |
| FE27 | same timestamp release/press replay re-enables | fixed offline | test_deadman_replayed_release_cannot_rearm |
| FE28 | bools act as mapping/limiter configuration | fixed offline | boolean_config_and_clock / velocity_malformed / slew_boolean cases |
| FE29 | truthy string stop silently means stop | fixed offline | test_slew_strict_stop_boolean |
| FE30 | target None/int/string crashes len or isfinite | fixed offline | test_slew_malformed_target_types |
| FE31 | acceleration*dt underflows to division zero | fixed offline | test_slew_underflow_does_not_divide_by_zero |
| FE32 | huge finite target loses direction through overflow ratio | fixed offline | test_slew_finite_large_target_retains_direction |
| FE33 | PID finite extremes produce nonfinite state | open | next round derived-arithmetic campaign |
| FE34 | filter finite extremes contaminate future estimates | open | next round transaction/rollback tests |

These findings concern disconnected experiments. Tests establish only the stated
pure-Python behavior, not a headset deadman, a physical servo, or vehicle control.
