# Frontend / XR charter

Own read-only telemetry presentation, Quest HUD usability, local offline
documentation navigation and explicit stale/unknown/mock states. Produce pure
Python contract logic and static browser assets without command publishing.

Success: malformed data never becomes trusted telemetry; stale status clears
numeric values; keyboard access and labels are reviewable; every claim separates
source tests from untested Quest/browser behavior. Acceptance requires Windows
unittest plus static checks; browser usability remains a human check until observed.

Red-team mandate: challenge timestamps, replay, booleans, enormous payloads,
misleading acknowledgement labels, accessibility and unintended command surfaces.
Record findings in redteam_roundN.md with executable regressions when applicable.

Integration boundary: new offline helpers are not live vehicle safeguards.
No ROS publishers, FC parameters, routing, altitude or live gesture changes.
