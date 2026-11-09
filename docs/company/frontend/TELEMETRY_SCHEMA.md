# Telemetry envelope v1 (offline experiment)

The new `telemetry_contract.py` helper accepts exactly seven fields. It is not
yet connected to the existing mock server or browser and introduces no transport.

| Field | Contract | Failure presentation |
| --- | --- | --- |
| schema | integer 1, bool forbidden | INVALID, all values unknown |
| mock | exact bool | INVALID |
| age | finite nonnegative seconds at source export | INVALID |
| mode | 1–64 characters, no ASCII controls | INVALID |
| battery | finite numeric percentage in [0,100], bool forbidden | INVALID |
| deadman | exact bool, descriptive only | INVALID |
| acks | list of at most 30 strings, each at most 256 characters | INVALID |

Source age plus locally elapsed time must be strictly less than a caller-provided
freshness limit. The helper imposes no operational threshold. Local receive time
and current time must use the same monotonic clock; wall-clock timestamps cannot
be substituted. A source lying about age remains undetectable without an
authenticated acquisition-time chain. A fresh packet is not proof of a fresh FC.

HTML-like text remains text. Consumers must use textContent or equivalent escaping.
Acknowledgements mean service acceptance only; this envelope cannot certify
altitude, landing, arming state, or flight safety.
