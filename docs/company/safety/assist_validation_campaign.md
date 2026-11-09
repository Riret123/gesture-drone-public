# R04 S05 - sensor assist validation campaign
No-flight rig: independently measure sensor-to-plane distance and target/camera motion while recording synchronized flow, range, tilt and exposure time. Include textured/plain floors, reflective/absorbing surfaces, inclined/stepped surfaces, moving texture, rotational motion, vibration and deliberate range dropout.

Compare estimate error versus ground truth by condition and accepted/rejected status. Establish angular-flow convention and rotation compensation separately; do not tune against the same data used to claim accuracy. Test cross-sensor timestamp offset intentionally.

Before any later integration, define failure response, sensor disagreement handling, independent altitude evidence and controller abort/reacquisition policy. This run neither authorizes nor performs such integration.
