# R01 E01 - hardware evidence ledger
| Interface | Known from source | Missing evidence | Release gate |
| --- | --- | --- | --- |
| Orange Pi companion | target named Orange Pi 5 Pro | exact board revision, supply ratings, image, thermal conditions | owner photographs and manufacturer revision documents |
| Flight controller | target named AERO SELFIE H743 | exact pinout, firmware revision, serial voltage and configured port | unpowered pinout review and isolated configuration capture |
| Camera | OpenCV index 0 | physical sensor, interface, capture latency, lens | index-to-device identity and calibration bundle |
| Rover MCU | ESP32/Pico concept | chosen part and board revision | choose one board before wiring |
| Driver/motors | conceptual H-bridge and geared pair | stall current, supply limits, dissipation | measured/vendor evidence and reviewed fuse design |

All rows remain unverified; no guessed pin numbers or part ratings. Existing launch serial device is a placeholder, not wiring evidence.
