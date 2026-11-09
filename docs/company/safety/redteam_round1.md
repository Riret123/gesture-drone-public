# Safety red team - round 1
| ID | Attack | Status and evidence | Next action |
| --- | --- | --- | --- |
| S01 | Green tests imply real flight permission | fixed wording: release_gates separates A through D; round1_review denies permission | later document checker should enforce evidence labels |
| S02 | New quality defaults silently change live flight | fixed: no constructor defaults and no live imports; quality_experiment discloses fixtures | maintain boundary regression |
| S03 | Receive freshness claimed as capture freshness | fixed claim only; latency_budget exposes distinction | functional gap V07 OPEN |
| S04 | Arbitrary numeric FMEA creates false confidence | fixed: hazard_register explicitly leaves probabilities unknown | maintain qualitative register |
| S05 | Human preflight checkbox represented as sensor truth | fixed specification: preflight_evidence_plan requires provenance | R02 evidence record schema |
| S06 | Treat physical/legal attacks as closed by unit tests | fixed traceability states external evidence remains open | avoid test-count inflation |
| S07 | Unknown source bypasses new observation policy via old controller | OPEN by design: observation policy is not wired to controller | no live safety claim; offline integration fixture later |

No legality, certification, physical safety or operational risk acceptance is determined. Current documentation is a review artifact, not an approved flight procedure.
