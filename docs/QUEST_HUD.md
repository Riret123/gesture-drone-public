# Quest 2 camera HUD

Serve the static page from the workspace: `python3 -m http.server 8090 --directory quest`.
On the Quest browser open `http://BOARD_IP:8090` and enter
`http://BOARD_IP:8080/stream`. Run `python3 video_stream_server.py --port 8080 --camera 0`
on the board separately. The video server and gesture node each open camera 0;
use separately unless the camera stack has been explicitly tested for sharing.

The large, responsive monoscopic view is suitable for a headset browser and a
future WebXR overlay. This is not an immersive WebXR session implementation.
Fullscreen is optional. MJPEG has unknown latency; loaded does not mean fresh.
No attitude, altitude, connection-to-FC, or live-flight claims are displayed.
HTTP on a local network supports this basic viewer; a future WebXR session needs
a secure context and tested Quest browser support. HTTPS pages may block HTTP video.

Deadman design only: any future command transport must require a continuously
held controller trigger, an explicit enable step, a short server-side lease,
sequence numbers, and validated timestamps. Release, tracking loss, focus loss,
XR session end, or lease expiry must revoke authority and request a tested hold,
then land policy. Browser events alone are insufficient: the receiver must enforce
expiry. Emergency landing must have an independent pilot-accessible route.
Do not enable arming or takeoff from mere page load, gestures, or connection.

This page has no command transport, ROS bridge, flight buttons, or deadman
implementation. It sends no flight commands. Validate visual comfort, frame
freshness and browser behavior on Quest before any operational use.
