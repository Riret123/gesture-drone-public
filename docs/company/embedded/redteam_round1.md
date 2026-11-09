# Embedded red team - round 1
| ID | Attack | Status and evidence | Next action |
| --- | --- | --- | --- |
| E01 | Named board implies a known power rating | fixed documentary claim: hardware evidence ledger marks exact revision and ratings missing | owner evidence still OPEN |
| E02 | UART wiring assumes voltage tolerance | fixed documentary scope: wiring_review blocks blank voltage evidence | no physical compatibility validated |
| E03 | Average current hides simultaneous startup/stall | fixed method: power_budget_method requires separate worst-case rows | R02 executable uncertainty-aware budget |
| E04 | Software stop presented as physical isolation | fixed claim: rover_stop_architecture separates watchdog and disconnect | schematic/backfeed proof OPEN |
| E05 | Unrendered CAD treated as structurally safe | fixed claim: cad_review_plan requires geometry/fit/load evidence | R02 parameter geometry checker |
| E06 | Battery information missing yet budget says pass | OPEN: no executable budget exists | R02 unknown values produce unknown result |
| E07 | Power disconnect leaves USB/UART backfeed | OPEN physical hazard; wiring_review records it | owner schematic/continuity review, no powered test here |

Documentary corrections do not count as electrical verification. Unit tests can validate calculation contracts but cannot validate wiring or disconnect efficacy.
