# R04 V05 - candidate receiver clock discipline
Every CandidateGate call validates now before examining the frame. Finite nonreversed evaluation time advances receiver clock even when the frame is missing or rejected. This prevents a later call from rewinding time to make data appear fresh. Invalid or reversed clocks reject without resetting.

Candidate-level and CaptureGate clocks can differ because only selected candidates reach CaptureGate; the outer gate must therefore enforce its own clock. Both clocks originate at the same experiment caller. A new gate remains a privileged owner action and must not be triggered by payload data.

Age comparisons remain inclusive at the configured limit and reject beyond it, with no added floating-point tolerance.
