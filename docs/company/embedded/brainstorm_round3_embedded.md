# R03 brainstorm - embedded
Producing role: five new proposals. Scores are qualitative internal votes, not market statistics. Each dimension is 1-5: safety value, evidence value, feasible offline implementation. Equal total scores prefer concrete unresolved attacks.
| ID | Idea / acceptance | Safety | Evidence | Feasibility | Total |
| --- | --- | ---: | ---: | ---: | ---: |
| E-B01 | Piecewise transient arithmetic: Compute explicit duration/peak/RMS/energy from synthetic source-current segments. | 5 | 4 | 4 | 13 |
| E-B02 | Shared rail dependency graph: Reject cycles and double-counting; model combined converter efficiency separately. | 4 | 4 | 2 | 10 |
| E-B03 | Parameterized hole-layout validator: Check edge distances and overlap before producing new CAD variants. | 4 | 4 | 4 | 12 |
| E-B04 | Power isolation truth table: Enumerate battery/USB/serial feed combinations and unknown backfeed states. | 5 | 5 | 3 | 13 |
| E-B05 | Encoder plausibility offline checker: Detect frozen/reversed counts under synthetic motion without motor actuation. | 4 | 4 | 3 | 11 |

Selected for this role group: bounded duplicate-tag selection (V-B01/VR-B01), transient waveform arithmetic (E-B01/ER-B01), and session-bound evidence (S-B01/SR-B01). These close specific open attacks with executable counterexamples. Other proposals stay on the evidence backlog; no claim of implementation.
