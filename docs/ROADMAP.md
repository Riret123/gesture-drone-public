# Validation roadmap

| Phase | Work | Exit evidence |
| --- | --- | --- |
| Offline simulation | fixtures, invalid telemetry, timing, landing fault injection | portable suite passes; reproducible seeds and failure cases recorded |
| Isolated SITL | calibrated adapters, command arbitration, stale-state rejection | logs prove ordering, hold/land/RTL behavior, disconnect response and verified altitude |
| Unpowered bench | board identity, serial levels, mounting and load review | props removed, motor power disconnected; wiring checklist reviewed; no arming |
| Powered rover only | estop, watchdog, localization, wheel guards | measured stopping distance; lost-link stop; drone kept unpowered |
| Tethered flight review | qualified operator, approved site, airspace, independent controls | separate authorization, test plan and FC failsafe validation; not authorized by this repository |
| Free flight | restricted envelope, observer, recovery procedures | independently approved results and measured failure response |
| Stationary landing rover | calibrated fiducial pose, velocity, contact sensor | SITL acceptance and prior flight phases passed; measured landing error and contact verification |
| Moving landing rover | relative motion, occlusion, wind and abort corridor | documented speed/wind limits, fault trials, independent approval |

Never skip phases on the strength of toy simulation or unit-test counts. Integration
work must review all proposed mode, timeout, altitude, threshold, frame and routing
changes explicitly. No hardware flight authorization is given here.
