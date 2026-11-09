# R02 V05 - prior attack closure
V07 old exposure/fresh receive: optional CaptureGate now checks total exposure-to-evaluation age; test_v07_old_exposure_with_fresh_receive_rejects proves rejection of the counterexample. Closure is conditional on true same-domain capture timestamps.

V08 repeated/reordered frames: accepted sequence and capture time must both increase; test_v08_replay_and_reordering and test_higher_sequence_with_repeated_or_reversed_capture_rejects prove the policy. New session data cannot reset a receiver; test_session_cannot_reset_receiver.

V09 false confidence remains OPEN: numeric metadata cannot establish empirical detector uncertainty. V02 identity metadata remains unauthenticated. Wrong physical calibration with a matching string still passes by design; requires measured calibration manifest review.
