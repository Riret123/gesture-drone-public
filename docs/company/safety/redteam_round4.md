# Safety red team - round 4
| ID | Attack | Status/evidence | Next |
| --- | --- | --- | --- |
| S22 | Slant range used directly as vertical height | fixed arithmetic; test_tilt_uses_cosine_not_slant_as_height | physical beam/plane assumptions OPEN |
| S23 | Truthy rotation-compensated flag bypasses prerequisite | fixed; test_uncompensated_rotation_and_nonplanar_surface_reject | no actual compensation measurement |
| S24 | Low/NaN quality or high flow still yields speed | fixed; test_range_tilt_quality_and_flow_envelopes | detector quality calibration OPEN |
| S25 | Range and flow sampled at different times but share receive time | OPEN: sample has no individual capture stamps | R05 synchronized sample envelope |
| S26 | Negative/unknown lidar return treated as altitude | fixed reject; range envelope tests | actual lidar return semantics external |
| S27 | Underflow produces zero estimated speed despite nonzero flow | OPEN numeric edge | R05 conservative underflow check |
| S28 | Correct arithmetic interpreted as descent clearance | fixed wording only, no output command | downstream integration remains forbidden here |

R03 S19 fixed. No certification, legal authorization, sensing accuracy or hardware flight is claimed.
