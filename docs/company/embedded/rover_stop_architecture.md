# R01 E04 - rover stop architecture
The existing firmware is a disabled concept, not a verified drive controller. Review three independent layers: command age/watchdog rejection, MCU output default-to-disabled behavior, and a physical motor-power disconnect reachable without entering wheel pinch zones. CRC detects corruption and does not authenticate commands.

Define startup, reboot, brownout, link-loss and malformed-message states as disabled output. A stop command is not proof of zero wheel speed: inertia, slope and driver fault can keep motion. Before a moving-pad experiment, measure stopping distance on representative surfaces and loads with no aircraft present under a separately authorized rover-only procedure.

Current blocker: no selected driver or wiring. No pin configuration or motor test is introduced.
