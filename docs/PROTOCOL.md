# Rover protocol v1 (offline experimental)

One UTF-8 JSON object per UDP datagram, or per newline on serial. Maximum 1024
bytes excluding serial newline. Fields are exactly: version (integer 1), seq
(unsigned 32-bit), mode (hold/follow/return_home), linear (m/s, +/-0.2), angular
(rad/s, +/-1), checksum (8 lowercase hex CRC32 digits). No extra or duplicate keys.
CRC32 covers all fields except checksum, JSON sorted keys, compact separators,
UTF-8, no NaN. Use the Python encoder as the canonical serializer; numeric lexical
forms matter to CRC. No timestamp from a remote clock is trusted.

Receiver must reject corruption, old/duplicate sequences, unknown version and
out-of-range values. Sequence wrap requires an explicit stopped session reset;
do not infer reset from a low sequence. Only fresh accepted packets renew the
local 500 ms watchdog. Hold means zero motor output regardless of velocity fields.
UDP loss/reordering is expected. CRC does not authenticate commands: isolate links;
do not deploy this protocol as a secure remote flight-control channel.

Modes describe intent; the receiver must not blindly enable follow or home without
localization and independent safety checks. No drone actuation is specified.
Firmware skeleton is deliberately disabled until a driver is reviewed.
