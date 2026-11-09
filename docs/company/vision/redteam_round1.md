# Vision red team - round 1
Reviewer role is simulated separately from the producing role; these are actual interface attacks, not independent external certification.

| ID | Attack | Status and evidence | Next action |
| --- | --- | --- | --- |
| V01 | Replay old observation or send future/nonfinite clock | fixed for receive age; test_v01_stale_boundary_and_future_clock | capture age remains V07 |
| V02 | Use another camera/calibration or boolean ID | fixed; test_v02_identity_and_boolean_id | immutable calibration manifest next |
| V03 | Supply malformed, NaN, infinite or enormous position | fixed; test_v03_nonfinite_and_wrong_dimension_pose | exercise randomized combinations |
| V04 | Lie with negative/boolean quality values | fixed syntactically; test_v04_quality_metrics_cannot_be_truthy_or_negative | empirical quality calibration unverified |
| V05 | Pose behind camera or outside configured range | fixed; test_v05_depth_envelope_is_inclusive | physical range envelope unverified |
| V06 | Change accepted pose by mutating input list | fixed; test_valid_snapshot_is_immutable_copy | input construction still trust-boundary only |
| V07 | Deliver an old camera exposure with fresh receive time | OPEN: current contract cannot detect this | R02 capture provenance contract |
| V08 | Replay same accepted frame repeatedly within age interval | OPEN: gate has no sequence memory | R02 monotonic session/sequence gate |
| V09 | Report tiny uncertainty for a wrong but plausible pose | OPEN: detector estimate not independently validated | ground-truth campaign; no dummy test closure |

No real images, detector accuracy or physical calibration validated. R02 must close V07/V08 in an optional separate gate without claiming live integration.
