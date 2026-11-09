# R04 V03 - prior attack fixes
V21: CandidateGate now validates every candidate receive time as finite, nonnegative and nonboolean before grouping. A None first distractor can no longer act as an uninitialized sentinel. Regression test_v21_invalid_first_distractor_receive_time_never_acts_as_sentinel.

V22: CandidateGate now maintains its own finite monotonic evaluation clock before frame validation. Rejected/missing/ambiguous frames cannot hide a clock rewind. Regression test_v22_rejected_frame_still_advances_receiver_clock.

V16: separate MotionGate rejects implausible position innovations with explicit experiment limits. test_v16_pose_jump_rejects_without_moving_anchor exercises a false jump then valid recovery. It does not solve target identity or calibration.
