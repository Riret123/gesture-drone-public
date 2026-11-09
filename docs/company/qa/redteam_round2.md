# QA red team: round 2

| ID | Attack | Status | Needed evidence |
| --- | --- | --- | --- |
| Q-R02-1 | Fixed-seed tests generate only small ordinary numbers. | open | log-scale generated values and precision-boundary campaign |
| Q-R02-2 | CLI filesystem behavior is mocked, actual board file paths untested. | blocked | Linux installed command and file permissions |
| Q-R02-3 | Source docs could drift from checked-in example durations. | fixed | checked-in example duration/distance tests |
| Q-R02-4 | Existing module tests import paths globally; focused invocation may fail. | fixed | each mission test now bootstraps source path |
| Q-R02-5 | Existing CI workflow written earlier does not prove remote green CI. | blocked | actual CI run URL required, no git commands permitted here |
| Q-R02-6 | No independent output sample parser checks finite positions and exact schema. | open | report contract validator round 03/04 |

Prior unresolved: Q-R01-5 installed package verification.
