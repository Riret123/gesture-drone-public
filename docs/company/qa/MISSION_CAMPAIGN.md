# Mission acceptance campaign

Run complete Windows suite after every change:

```powershell
python -B tests/run_all.py
```

Focused parser/simulator/CLI tests may be run independently:

```powershell
python -B -m unittest discover -s tests -p "test_mission*.py" -v
```

| Campaign | Oracle | Evidence |
| --- | --- | --- |
| ENU geometry | independent 3-4-5 leg length and midpoint | test_one_leg_independent_distance |
| Height | one metre rise from nonzero start | test_vertical_leg |
| Dwell | exact travel/dwell/next-leg join times | test_dwell_boundaries |
| Degenerate plan | zero travel keeps dwell; all-zero plan one complete sample | test_zero_length_leg_still_dwells, test_zero_duration_plan |
| Resource limits | total travel+dwell capped; sample cap before allocation | test_duration_budget_includes_dwell, test_sample_budget_before_allocation |
| Precision | reject positive unrepresentable clock increments | three subnormal/subresolution tests |
| Random valid paths | 30 runs, 5 points, fixed seed 12345, speed and fence invariants | test_seeded_paths_stay_inside_convex_fence |
| Largest valid plan | 256 longest names, precision floats roundtrip under byte cap | test_maximum_valid_plan_fits_ingestion_limit |
| Byte reading | short reads assembled; byte limit enforced | test_short_reads_do_not_truncate_json, test_reader_never_requests_unbounded_read |
| CLI authority | no send flag, explicit nonphysical summary, bounded failures | test_unknown_send_option_is_rejected and CLI tests |

This is not a fuzzing substitute for all schemas, not a physics validation and
not installed-package verification. Linux colcon/ament, external CI, ROS/SITL and
board runtime remain blocked pending target access. No tests here arm motors.
