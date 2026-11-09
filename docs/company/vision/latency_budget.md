# R01 V05 - latency and freshness analysis
An accepted local-receive timestamp does not prove a current camera exposure. Total observation age includes exposure/readout, camera buffering, inference, queueing, transport and dispatch. Measure each boundary with the same clock where possible; clock-domain conversion requires offset and uncertainty evidence.

The initial gate bounds receive-to-evaluate age only. Delayed but newly received frames remain an open attack. A later adapter must preserve capture sequence and freshness provenance and reject out-of-order samples. Bounded queues and deliberate frame dropping can reduce delay but need measurement under CPU thermal throttling and camera stall.

Never renew a landing lease from a repeated stale pose. The current implementation has no lease and is not connected to the landing controller.
