# Vision red team - round 4
| ID | Attack | Status/evidence | Next |
| --- | --- | --- | --- |
| V24 | Rejected pose jump moves temporal anchor | fixed; test_v16_pose_jump_rejects_without_moving_anchor | randomized trajectories |
| V25 | Gap automatically reacquires unrelated target | fixed; test_gap_requires_new_gate_not_automatic_reacquisition | coordinator reset semantics needed |
| V26 | Mutable initial position rewrites anchor | fixed; test_mutable_input_is_copied | keep snapshot invariant |
| V27 | Extreme opposite finite coordinates overflow distance | fixed; test_numeric_overflow_and_invalid_configuration | no silent infinity acceptance |
| V28 | Slowly drifting false pose passes motion envelope | OPEN intrinsic limitation | independent target/quality evidence |
| V29 | Multiple independently accepted gates lack one fail-closed coordinator | OPEN architecture gap | R05 offline integrated observation pipeline |
| V30 | Equivalent candidate orders change result | OPEN test coverage | R05 permutation campaign |

R03 V21/V22 fixed with direct regressions. R01 false-confidence and R02 clock-origin assumptions remain open. No real perception performance claim.
