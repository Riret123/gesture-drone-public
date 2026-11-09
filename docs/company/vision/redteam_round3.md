# Vision red team - round 3
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| V17 | Duplicate identical target detections bypass ambiguity | fixed; test_v15_duplicate_target_rejects_even_if_identical | keep ordering campaign |
| V18 | Thousands of malformed candidates cause unbounded iteration | fixed for explicit tuple count; test_bounded_before_candidate_validation | input parser size before tuple construction is external |
| V19 | Wrong-camera distractor mixed into valid target frame | fixed; test_mixed_camera_calibration_and_receive_reject | origin authenticity still open |
| V20 | Ambiguous frame consumes sequence and blocks corrected frame | fixed; duplicate test then accepts original sequence | stateful randomized campaign |
| V21 | First candidate receive time None is used as uninitialized sentinel | OPEN: candidate timestamp needs finite check before equality grouping | R04 fix with regression |
| V22 | Rejecting frames skips receiver clock tracking | OPEN integration nuance: CandidateGate rejects before CaptureGate sees now | R04 explicit candidate-level clock discipline |
| V23 | Unselected distractor supplies malformed pose/quality | deferred: only target quality is used; unrelated metadata policy must be explicit | document/validate enough source metadata |

R02 V15 now fixed at metadata selection level. R01 V09, R02 V14/V16 remain open. No external detector validation.
