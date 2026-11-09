# Embedded red team - round 2
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| E08 | Duplicate named rail hides bookkeeping mistake | fixed; test_duplicate_empty_or_unvalidated_load_list_rejects | graph topology later |
| E09 | Unknown efficiency assumed ideal | fixed; test_e06_unknown_values_never_create_passing_budget | preserve unknown status |
| E10 | Huge finite operands overflow total to infinity | fixed; test_boundary_and_overflow returns INVALID | randomized numeric campaign |
| E11 | Scalar peak current omits pulse duration | OPEN: transient_limits explicitly blocks hardware selection | R03 transient profile prototype |
| E12 | Shared converter loss counted independently at wrong operating point | OPEN: rail_topology_review exposes API assumption | topology model design |
| E13 | Regenerative braking pushes voltage above rail limits | OPEN: current scalar budget models consumption only | external driver/source evidence |
| E14 | Zero current valid for intentionally disabled load but rejected | deferred design choice: omit disabled loads explicitly; no zero-as-unknown | document operating-case selection |

R01 E03/E06 now fixed arithmetically; E07 physical backfeed remains open. No electrically verified hardware claim.
