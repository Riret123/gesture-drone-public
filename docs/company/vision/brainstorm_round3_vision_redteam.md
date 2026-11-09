# R03 brainstorm - vision_redteam
Red-team: five new proposals. Scores are qualitative internal votes, not market statistics. Each dimension is 1-5: safety value, evidence value, feasible offline implementation. Equal total scores prefer concrete unresolved attacks.
| ID | Idea / acceptance | Safety | Evidence | Feasibility | Total |
| --- | --- | ---: | ---: | ---: | ---: |
| VR-B01 | Attack first-valid detection selection: Duplicate target detections with incompatible poses must not select arbitrarily. | 5 | 5 | 5 | 15 |
| VR-B02 | Attack capture time forgery: Expose that monotonic metadata alone cannot authenticate true exposure time. | 5 | 5 | 2 | 12 |
| VR-B03 | Attack reacquisition after motion jump: Require reset policy to avoid silently accepting a new physical target. | 5 | 4 | 3 | 12 |
| VR-B04 | Attack quality estimate circularity: A detector residual cannot be its own independent calibration evidence. | 4 | 5 | 2 | 11 |
| VR-B05 | Attack resize/crop calibration reuse: Invalidate old intrinsic calibration when image geometry changes. | 5 | 5 | 3 | 13 |

Selected for this role group: bounded duplicate-tag selection (V-B01/VR-B01), transient waveform arithmetic (E-B01/ER-B01), and session-bound evidence (S-B01/SR-B01). These close specific open attacks with executable counterexamples. Other proposals stay on the evidence backlog; no claim of implementation.
