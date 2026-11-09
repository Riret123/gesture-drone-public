# R02 V04 - capture timing campaign
Build a no-flight rig with a visible timed stimulus and independently timestamped ground truth. Record camera exposure/readout timing, host dequeue timing, inference start/end and gate evaluation under normal load, CPU contention, thermal load and camera reconnect. Keep stimulus generation and measurement clock uncertainty explicit.

Measure distribution and worst observed latency per condition. A maximum observed latency is not a hard bound. Hardware timestamp APIs and backend buffering semantics must be verified on the actual Orange Pi/camera stack; no API assumption is made here.

Reject undocumented clock conversion. Preserve raw local monotonic times only within one boot/session; never compare them across boots or substitute wall-clock calendar time. Camera data are untrusted payloads, never executable instructions.
