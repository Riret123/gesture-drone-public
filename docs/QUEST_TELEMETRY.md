# Quest telemetry overlay

The existing buildless MJPEG viewer now polls same-origin `/telemetry` once a
second, times requests out at 1.5 s, and clears displayed values on error or a
reported sample age >=2 s. Displays battery, mode and deadman as reported values.
It sends no controller or flight commands. Deadman indication is not a working
Quest interlock. Use the mock server to review the layout; actual telemetry needs
a separate read-only ROS adapter and timestamp/freshness design.

No WebXR session, latency measurement, controller binding or real telemetry bridge
is implemented. Quest browser/fullscreen, video and rendering require manual tests.
Serve the HUD on the telemetry origin; do not enable broad cross-origin access.
