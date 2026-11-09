# Vision red team - round 2
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| V10 | Increment sequence but repeat exposure timestamp | fixed; test_higher_sequence_with_repeated_or_reversed_capture_rejects | retain regression |
| V11 | Poison sequence with rejected high-number wrong-camera sample | fixed; test_invalid_metadata_does_not_consume_sequence | randomized stateful campaign |
| V12 | Input switches session to reset replay state | fixed; test_session_cannot_reset_receiver | restart persistence remains open |
| V13 | Rewind receiver time to freshen stale sample | fixed; test_time_ordering_and_clock_reversal | rejected finite call advancement documented |
| V14 | Capture time is from unsynchronized remote device | OPEN: same-domain precondition cannot be established by floats | provenance manifest/checklist |
| V15 | Two competing tag detections both look valid | OPEN: no uniqueness selection | R03 multi-tag ambiguity policy |
| V16 | False high-quality pose leaps across image | OPEN: gate has no temporal motion bound | R03 conservative innovation gate design |

R01 V07/V08 are conditionally fixed in a separate optional offline gate; R01 V09 remains unverified. No detector or live-flight claim.
