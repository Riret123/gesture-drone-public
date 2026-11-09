# R04 V02 - motion gate failure analysis
A sudden false pose can exceed the envelope and reject, but a drifting false pose may remain inside it. A legitimate fast rover or camera rotation can exceed an overly narrow envelope. Therefore rejection is an observation-quality result, not proof of a stationary or dangerous physical object.

After a long gap the old anchor may no longer represent the same physical target. The gate requests reacquisition_required; input cannot silently reset it. A future offline coordinator must stop descent proposals and require an explicit target/reacquisition process. Do not merely instantiate a fresh gate on every rejection.

Relative speed must include drone, rover and measurement dynamics in a common frame; camera rotation changes observed position even when world translation is small.
