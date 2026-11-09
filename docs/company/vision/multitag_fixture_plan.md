# R03 V02 - ambiguity fixture design
Fixtures: one target; target plus distractor; target absent; two identical target detections; two incompatible target poses; mixed camera; mixed calibration; mixed receive times; oversized candidate set; malformed ID and invalid target quality. Each case has a named test in test_landing_candidates.py.

Physical campaign must include separate copies of the same printed tag, reflections and overlapping tags. A single configured numeric ID is not a globally unique physical landing pad. No unit-test case establishes detector behavior under reflections or motion blur.

For later multi-marker boards, change the contract deliberately: board geometry, marker family and unique transforms need verification. Do not loosen duplicate rejection by averaging incompatible poses.
