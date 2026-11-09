# R01 S02 - release gates
Gate A: pure Python tests and static review. Permits further offline work only.
Gate B: reviewed hardware identity, wiring, power and calibration evidence. Permits only the separately approved bench scope; never implies arming permission.
Gate C: isolated SITL with no physical FC or other ROS command participants, endpoint recorded and independent observer. Live integration script is SITL-only and can arm the simulated vehicle.
Gate D: separately reviewed legal/site authorization, independent pilot, FC failsafes, exclusion zone and emergency plan. This run cannot grant this gate or real flight permission.

A gate is evidence-specific and invalidated by relevant changes. Passing unit tests cannot skip B-D. This run changes no live safety parameters or MAVLink routing.
