# R02 S05 - offline regression matrix
| Feature | New counterexample | Executable evidence | Uncovered external evidence |
| --- | --- | --- | --- |
| capture age | delayed exposure/fresh receive | test_v07_old_exposure_with_fresh_receive_rejects | clock provenance |
| capture ordering | increasing sequence/repeated exposure | test_higher_sequence_with_repeated_or_reversed_capture_rejects | authenticated source |
| power budget | simultaneous stall peaks | test_e03_simultaneous_peaks_are_not_averaged | actual current traces |
| unknown power | missing load/source value | test_e06_unknown_values_never_create_passing_budget | measured ratings |
| evidence origin | human checkbox for measurement | test_s05_human_checkbox_cannot_substitute_for_measurement | authenticity and quality |
| evidence age | expired/future timestamp | test_expired_future_and_invalid_times | persistent audit timestamp |

Full portable suite is run after every code/document batch; shared suite totals may increase while other roles work. No ROS/SITL/camera/hardware tests are implied.
