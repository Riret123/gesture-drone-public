# Safety red team - round 2
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| S08 | Empty requirements creates vacuous green preflight | fixed; test_empty_requirements_and_invalid_policy_cannot_pass_vacuously | preserve strict constructor |
| S09 | Human/simulation record substitutes for measured calibration | fixed metadata; test_s05_human_checkbox_cannot_substitute_for_measurement | artifact authenticity OPEN |
| S10 | Truthy string yes counts as passed | fixed; test_truthy_result_does_not_pass | randomized records |
| S11 | Old configuration evidence accepted after revision change | fixed metadata; test_wrong_scope_and_revision | revision assignment is human-owned |
| S12 | Duplicate records choose favorable last value | fixed; test_duplicate_invalid_and_missing_reference | immutable audit storage OPEN |
| S13 | Opaque reference points to fabricated evidence | OPEN: no content/authenticity verification | documented reviewer chain |
| S14 | Local monotonic time compared across reboots | OPEN precondition: same-session only | R03 explicit session identity |

R01 S05 has executable origin enforcement now; R01 S07 live bypass remains out of scope and explicitly open. Unit-test success is not flight approval.
