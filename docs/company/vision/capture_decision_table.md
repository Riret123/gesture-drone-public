# R02 V03 - capture decision table
| Condition | Reason | Consumes sequence? |
| --- | --- | --- |
| invalid receiver clock | invalid_clock | no |
| receiver clock reverses | clock_reversed | no |
| wrong session | wrong_session | no |
| boolean/negative/noninteger sequence | invalid_sequence | no |
| sequence no greater than accepted prior | replayed_or_reordered | no |
| exposure does not advance | capture_not_advancing | no |
| exposure exceeds total age bound | exposure_stale | no |
| metadata policy rejects | metadata reason preserved | no |
| all pass | metadata_valid | yes |

Evaluation time advances on any finite nonreversed call, including rejected data. This is intentional receiver-clock protection, not data freshness renewal. The output remains an immutable position tuple and no command.
