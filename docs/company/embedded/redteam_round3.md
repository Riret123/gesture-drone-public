# Embedded red team - round 3
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| E15 | Same peak hides a tenfold pulse duration | fixed arithmetic; test_e11_same_peak_different_duration_changes_energy | thermal model still absent |
| E16 | Idle gaps omitted from RMS denominator | fixed only when explicit zero segments supplied; test_rms_includes_known_zero_idle | missing intervals remain caller responsibility |
| E17 | Negative regeneration lowers consumption to create false pass | fixed reject; test_regeneration_rejects_consumption_only_model | external regeneration design open |
| E18 | Splitting identical waveform changes summary | fixed invariant; test_partitioning_constant_segment_preserves_result | randomized partition campaign |
| E19 | Tiny positive duration/current products underflow to zero | OPEN: conservative arithmetic should detect lost nonzero energy | R04 numeric edge regression |
| E20 | RMS limit treated as winding-temperature proof | fixed documentation only: transient_profile_contract denies thermal model | actual temperature measurement open |
| E21 | Arbitrarily many segments consume memory/time | OPEN: API bounds not configured | R04 explicit max segment contract |

No hardware is energized. R02 E11 partial closure is explicitly arithmetic; E12/E13 remain unverified.
