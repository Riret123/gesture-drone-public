# R04 S03 - disclosed assist fixtures
Unit fixtures use receive age 0.25 s, range 0.1-3 m, tilt maximum 0.5 rad, quality minimum0.5 and angular-flow vector bound1 rad/s. These are synthetic values selected to make arithmetic counterexamples readable. They are not measured device capabilities or approved flight limits.

At 2 m slant range and zero tilt, (0.1,-0.1) rad/s yields (0.2,-0.2) m/s in caller-defined camera-plane axes. At tilt0.5 rad the estimate uses cosine correction. This does not establish NED/ENU/body signs or compensation accuracy.

All limits are explicit arguments; malformed configuration raises rather than silently disabling a guard. Physical sensor and synchronization data remain verify tasks.
