# R04 S01 - optical flow and range assist model
`sensor_landing_assist` provides a pure-Python planar arithmetic experiment. Input is slant range, camera tilt, rotation-compensated angular flow, quality and local receive time. Explicit range/tilt/quality/flow/age limits bound the experiment. Height approximates range*cos(tilt); camera-plane speed approximates height*angular_flow under the declared small-angle planar model.

Output says MODEL_ESTIMATE with unverified_planar_model, never a control command or descent permission. Rotation compensation and planar-surface flags are strict boolean attestations; they are not measured by this module. Lidar multiple returns, reflectivity, flow axis signs, rotation estimation and camera/range synchronization remain external requirements.

No FC parameters, routing or live landing behavior changes.
