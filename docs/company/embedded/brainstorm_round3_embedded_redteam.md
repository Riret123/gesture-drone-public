# R03 brainstorm - embedded_redteam
Red-team: five new proposals. Scores are qualitative internal votes, not market statistics. Each dimension is 1-5: safety value, evidence value, feasible offline implementation. Equal total scores prefer concrete unresolved attacks.
| ID | Idea / acceptance | Safety | Evidence | Feasibility | Total |
| --- | --- | ---: | ---: | ---: | ---: |
| ER-B01 | Attack scalar peak-only budget: Identical peak amplitude with different duration must produce different energy. | 5 | 5 | 5 | 15 |
| ER-B02 | Attack negative-current regeneration: Consumption-only model must reject regeneration instead of hiding rail rise. | 5 | 4 | 4 | 13 |
| ER-B03 | Attack undefined disabled-load handling: Zero waveform samples need explicit semantics distinct from unknown demand. | 4 | 4 | 5 | 13 |
| ER-B04 | Attack impossible printed geometry: Min/max parameter combinations can merge holes or remove wall thickness. | 4 | 4 | 4 | 12 |
| ER-B05 | Attack connector identity ambiguity: Matching visual connectors do not establish pinout or voltage compatibility. | 5 | 5 | 2 | 12 |

Selected for this role group: bounded duplicate-tag selection (V-B01/VR-B01), transient waveform arithmetic (E-B01/ER-B01), and session-bound evidence (S-B01/SR-B01). These close specific open attacks with executable counterexamples. Other proposals stay on the evidence backlog; no claim of implementation.
