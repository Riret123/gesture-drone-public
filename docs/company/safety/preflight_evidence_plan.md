# R01 S05 - automated preflight evidence boundaries
An offline checklist can report missing evidence; it cannot inspect physical propellers, airspace, people, wiring or real FC behavior. Never convert a human checkbox into measured truth. Record evidence origin and age with every item.

Proposed categories: configuration identity; source isolation; FC connectivity/state freshness; calibration identity; localization/RTL capability; battery health; weather/site authorization; independent pilot; physical exclusion; emergency readiness. A missing required item blocks an offline readiness recommendation.

The live bridge does not consume these checks. Adding a report does not add an active guard. Keep the test script physically isolated from hardware regardless of any report result.
