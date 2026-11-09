# Manual board services

These are unexecuted Linux templates. They do not enable boot startup. They
require Bash, flock, timeout, systemd user services, ROS Jazzy and an existing
ai_env/install workspace. Confirm the actual Linux user and paths first.

1. Transfer the reviewed working tree to the board. Working-tree changes here
   are not published and cannot be retrieved by pulling a remote repository.
2. Build both packages using the deployment environment documented in AGENTS.md.
3. Copy scripts/board/drone-core@.service to ~/.config/systemd/user/ and copy
   core.env.example to ~/.config/gesture-drone/core.env; create directories first.
   Edit DRONE_WORKSPACE. Set a verified observation endpoint and keep mode observe.
4. Run `systemctl --user daemon-reload`. Do not enable units or lingering.
5. Source ROS and the workspace in the healthcheck terminal. Run
   `bash scripts/board/core.sh start mavros`, then the healthcheck action.
6. Camera preview: start camera, visit localhost:8080 on the board or a manually
   managed local tunnel. Stop camera before gesture. Both use the same flock.
7. Only for physically isolated SITL, set DRONE_MODE=sitl and the documented
   loopback UDP endpoint. Manually start bridge; observe five seconds continuously
   connected/disarmed, explicitly operator_reset in isolated SITL per SITL.md,
   then start gesture last. A camera gesture can then request simulated takeoff.
   Never use this path with a real FC.
8. Stop gesture, bridge, camera, then mavros explicitly using the stop action.
   Stopping processes sends no flight command; FC failsafes remain essential.
9. Collect to a new local directory outside source control using the collect
   action. Review/redact before sharing. No network settings or credentials are
   collected intentionally; arbitrary runtime log text can still be private.

Healthcheck reports process/topic/service observations, not readiness or an
acknowledged landing. Capture FC state and acknowledgements separately during
SITL. Services deliberately do not restart control nodes: restarting loses
debounce/command history. Every live bridge startup now requires observed
disarmed dwell and explicit reset before takeoff. No boot activation,
crash recovery or real-board execution has been validated here.
