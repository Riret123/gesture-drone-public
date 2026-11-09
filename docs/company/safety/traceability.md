# R01 S03 - requirement-to-test traceability
| Requirement | Attack | Evidence |
| --- | --- | --- |
| reject stale/future receive time | V01 | test_v01_stale_boundary_and_future_clock |
| exact source/tag/calibration identity | V02 | test_v02_identity_and_boolean_id |
| finite dimensioned pose | V03 | test_v03_nonfinite_and_wrong_dimension_pose |
| valid quality metrics within experiment limits | V04 | test_v04_quality_metrics_cannot_be_truthy_or_negative |
| configured depth envelope | V05 | test_v05_depth_envelope_is_inclusive |
| mutable input cannot rewrite result | V06 | test_valid_snapshot_is_immutable_copy |

These tests exercise metadata policies only. Physical false positives, voltage compatibility, propulsion isolation and legal permissions require external evidence and remain open. A documentary attack must get a documented verification procedure; it cannot honestly be closed by a dummy unit test.
