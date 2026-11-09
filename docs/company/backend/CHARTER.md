# Backend and flight-logic charter

Build deterministic pure-Python offline mission and swarm experiments. No module
may publish ROS commands, access a serial device, arm a vehicle, or alter the live
bridge. Constructor validation must protect direct callers as well as JSON users.

Own mission_*, swarm_*, policy_* modules and their tests. Record all proposed
parameters as simulator assumptions; defaults do not constitute flight tuning.
Red-team findings use B-Rxx-n identifiers; fixes require a reproducible failing
case and a regression. Performance claims need a defined model and measurement.

Each batch runs the complete portable suite. On regression, stop feature work,
repair, rerun, and report. No hardware, camera, SITL, or middleware success is
inferred from a successful Python test.
