# Embedded red team - round 4
| ID | Attack | Status/evidence | Next |
| --- | --- | --- | --- |
| E22 | Check centre inside plate but hole protrudes beyond edge | fixed; test_e05_hole_edge_not_centre_controls_clearance | geometric only |
| E23 | Duplicate holes accepted as separate fasteners | fixed; test_duplicate_and_impossible_plate | no fastening proof |
| E24 | Quadratic checking on huge hole list | fixed explicit64 concept limit; test_invalid_dimensions_centres_and_bound | document resource semantics |
| E25 | Nonzero tiny load reported as zero energy | fixed; underflow regression | scalar energy_budget has similar possible issue: OPEN |
| E26 | Use checker output as structural certification | fixed documentary scope only | actual material/load test OPEN |
| E27 | Planar checker ignores fastener head and tool clearance | OPEN model limitation | R05 clearance-envelope extension |
| E28 | Width/height accepted without thickness | explicit model choice; no structural calculation | thickness belongs future structural model |

R03 E19/E21 fixed. Physical backfeed, thermal and regenerative hazards remain open and no motors run.
