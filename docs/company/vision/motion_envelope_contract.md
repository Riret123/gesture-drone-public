# R04 V01 - observed motion envelope
`landing_motion.MotionGate` accepts explicit maximum relative speed, position allowance and maximum sample interval. It anchors the first finite 3D position, then compares Euclidean displacement against speed*elapsed_capture_time + allowance. Rejected samples do not move the anchor. Repeated/reversed capture times reject; excessive gap requires a new gate rather than automatic reacquisition.

The position allowance accounts only for a supplied experiment error envelope, not a measured statistical guarantee. First sample remains unvalidated by temporal consistency; slow false targets can pass. This gate is not integrated with CandidateGate, the landing controller or ROS.

Tests use 1 m/s, 0.125 m allowance and 1 s interval solely as synthetic values. No live safety parameter changes.
