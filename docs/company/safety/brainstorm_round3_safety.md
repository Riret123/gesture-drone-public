# R03 brainstorm - safety
Producing role: five new proposals. Scores are qualitative internal votes, not market statistics. Each dimension is 1-5: safety value, evidence value, feasible offline implementation. Equal total scores prefer concrete unresolved attacks.
| ID | Idea / acceptance | Safety | Evidence | Feasibility | Total |
| --- | --- | ---: | ---: | ---: | ---: |
| S-B01 | Session-bound evidence review: Require evidence session identity so reboot-local clocks cannot be compared. | 5 | 5 | 4 | 14 |
| S-B02 | Evidence change-impact map: Mark which configuration changes invalidate calibration/power/test artifacts. | 5 | 5 | 3 | 13 |
| S-B03 | Safety claim vocabulary checker: Flag hardware-ready claims lacking evidence labels in controlled documents. | 3 | 4 | 3 | 10 |
| S-B04 | Dual reviewer release record: Require named human review outside automated metadata completion. | 4 | 5 | 2 | 11 |
| S-B05 | Conservative failure-injection ledger: Record exact counterexample, expected state and residual assumptions. | 5 | 5 | 4 | 14 |

Selected for this role group: bounded duplicate-tag selection (V-B01/VR-B01), transient waveform arithmetic (E-B01/ER-B01), and session-bound evidence (S-B01/SR-B01). These close specific open attacks with executable counterexamples. Other proposals stay on the evidence backlog; no claim of implementation.
