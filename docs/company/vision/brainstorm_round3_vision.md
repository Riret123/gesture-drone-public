# R03 brainstorm - vision
Producing role: five new proposals. Scores are qualitative internal votes, not market statistics. Each dimension is 1-5: safety value, evidence value, feasible offline implementation. Equal total scores prefer concrete unresolved attacks.
| ID | Idea / acceptance | Safety | Evidence | Feasibility | Total |
| --- | --- | ---: | ---: | ---: | ---: |
| V-B01 | Reject duplicate expected-tag candidates in one frame: Build a bounded candidate selector; two matching tags must produce ambiguity, never first-wins. | 5 | 5 | 4 | 14 |
| V-B02 | Bound inter-frame pose innovation: Require experiment motion bound and elapsed time; avoid unverified dynamics claims. | 5 | 4 | 3 | 12 |
| V-B03 | Version physical marker manifests: Bind family, physical edge convention and measured size to calibration. | 4 | 5 | 3 | 12 |
| V-B04 | Stratify held-out detector evaluation: Split by session and marker, report false acceptance on marker-absent images. | 4 | 5 | 2 | 11 |
| V-B05 | Record rejection coverage by reason: Read-only count aggregation without renewing leases or admitting invalid data. | 3 | 3 | 5 | 11 |

Selected for this role group: bounded duplicate-tag selection (V-B01/VR-B01), transient waveform arithmetic (E-B01/ER-B01), and session-bound evidence (S-B01/SR-B01). These close specific open attacks with executable counterexamples. Other proposals stay on the evidence backlog; no claim of implementation.
