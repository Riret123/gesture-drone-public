# Backend red team: round 2

| ID | Attack | Status | Regression/target |
| --- | --- | --- | --- |
| B-R02-1 | Tiny positive travel underflows to zero time. | fixed in review | test_subnormal_travel_cannot_become_instantaneous |
| B-R02-2 | Tiny dwell after long travel silently disappears. | fixed in review | test_subresolution_dwell_cannot_silently_disappear |
| B-R02-3 | Assignment replaces mission while preserving old cached segments. | fixed in review | test_trajectory_cannot_be_accidentally_reconfigured |
| B-R02-4 | Short binary reads truncate input before parser sees remainder. | fixed in review | test_short_reads_do_not_truncate_json |
| B-R02-5 | Summary-only bypasses invalid sampling parameter types. | fixed in review | test_summary_only_still_validates_resource_configuration |
| B-R02-6 | Direct query on manually altered trusted Python object bypasses frozen fields. | known boundary | not a JSON threat; ORIGIN_AND_TRUST |
| B-R02-7 | Repeated `at()` is O(points), large swarm comparison could be costly. | open | bounded swarm count and benchmark before optimizing |

Prior unresolved: B-R01-2 structured field diagnostics.
