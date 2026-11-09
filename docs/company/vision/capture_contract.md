# R02 V01 - capture provenance extension
`landing_capture.CaptureObservation` wraps a validated metadata candidate with session ID, nonnegative integer sequence and local monotonic capture time. `CaptureGate` rejects mismatched sessions, repeated/lower sequences, nonadvancing capture times, capture-after-receive, old exposures and receiver clock reversal.

Capture and receive must be in the same clock domain before entry. The code does not estimate offsets. A new session requires constructing a new receiver from trusted experiment configuration; data cannot reset state. Only accepted observations consume sequence/capture state. Invalid input still advances the receiver's last evaluation clock to prevent rewinding evaluation time.

A forged increasing timestamp/sequence can pass: this is replay ordering, not authentication. No ROS wrapper imports this gate. Fixture age limit 0.3 s is an offline test value, not an approved landing threshold.
