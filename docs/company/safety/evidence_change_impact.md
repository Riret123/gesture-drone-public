# R03 S02 - configuration change impact
| Change | Evidence to invalidate or review |
| --- | --- |
| camera resolution/crop/focus | intrinsics, detector accuracy, latency, extrinsics if mount moved |
| camera mounting/bracket | extrinsics, vibration/deflection, physical clearance |
| marker print/size/family | metric scale, detector family, landing-pad identity |
| motor/driver/battery/regulator | current/thermal/fuse/wiring and stopping envelope |
| clock source/process restart | session identity, capture age and local evidence ages |
| software threshold/config | unit counterexamples, offline campaign and later SITL scope |

Changing a revision string is not enough: the responsible reviewer must enumerate affected artifacts. No automatic rule here authorizes hardware work.
