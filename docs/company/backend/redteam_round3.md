# Backend red team: round 3

| ID | Attack | State | Evidence/next step |
| --- | --- | --- | --- |
| B-R03-1 | Equal +0/-0 and int/float missions get different hashes. | fixed | test_equal_numeric_representations_same_identifier |
| B-R03-2 | Two paths cross between ticks despite safe endpoints. | fixed for toy model | test_perpendicular_crossing_between_ticks |
| B-R03-3 | Prestart or finished aircraft ignored by comparison. | fixed for toy occupancy | prestart/finished/stationary tests |
| B-R03-4 | Global delay rounds away a tiny positive path interval. | fixed | test_global_delay_cannot_erase_positive_interval |
| B-R03-5 | Maximum 32-agent plan is slow enough to miss control deadlines. | limitation | measured9.682s, module offline only; no control deadline claim |
| B-R03-6 | Pairwise report has no executable schema validator. | open | report consistency/finite-field validator next round |

Prior open: structured field diagnostics and output byte cap. No flight-safety
parameter or live threshold change was made.
