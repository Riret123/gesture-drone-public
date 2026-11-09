# R01 V01 - tag observation contract
Implementation: `src/gesture_control/gesture_control/landing_observation.py`.

A `TagObservation` is one already-computed pose and quality summary. `position_m` uses camera optical axes: x right, y down, z forward. It is not NED, ENU, drone body or a MAVROS setpoint. The gate never transforms coordinates. The existing `frames.transform` requires measured extrinsics before position use elsewhere.

`received_s` is local monotonic receive time. It does not prove exposure time; transport buffering can make a newly received frame old. Remote timestamps must not be copied into this field. `camera_id` and `calibration_id` must exactly match the experiment configuration. `tag_id` rejects booleans despite Python's boolean/integer relationship.

Output copies accepted position into a tuple so later mutation of the input list cannot change the decision. Rejection has no position. Acceptance means metadata validity only: plausible false detections and incorrect-but-matching calibrations remain undetectable here.
