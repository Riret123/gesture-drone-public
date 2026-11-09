# Orange Pi 5 Pro measurement and tuning worksheet

These are local prototype measurement steps, not measured board specifications.
No OS governor, scheduling priority, FC parameter, failsafe or network change is
required. Use motor power disconnected and the bridge stopped for camera work.

1. Record the actual board revision, OS/kernel, CPU architecture, power supply,
   cooling, camera interface, Python, OpenCV and MediaPipe versions. Confirm the
   required `mp.solutions.hands` API imports in the same interpreter used by ROS.
2. Establish a baseline with one camera owner. Current camera settings request
   640 by 480 at 30 fps and model complexity 0; record negotiated settings and
   delivered frame intervals. A successful `set()` is not measurement evidence.
3. Record capture/dequeue, inference, decision, publication, bridge receipt,
   submission, response and observed FC-transition times on a common monotonic
   clock where possible. Dequeue time does not prove exposure age. Record clock
   uncertainty where components use different clocks.
4. Measure idle and sustained camera load, then a controlled contention run.
   Record temperature, throttling observations, CPU load, memory and frame gaps
   using the actual OS's available read-only tools. Keep raw captures private.
5. Summarize p50, p95, maximum, sample count, dropped/invalid frames and measurement
   duration. Use `core_latency.LatencyLedger` for bounded offline summaries; it
   does not acquire timestamps automatically or enforce a flight deadline.
6. Change one camera parameter at a time in a copy of the reviewed configuration.
   Validate the schema and rerun the portable suite. Camera dimensions are bounded
   to width 160..1920 and height 120..1080, fps 5..60, model 0 or 1. These are
   accepted configuration bounds, not evidence that every combination performs.
7. Replay identical held-out sessions before and after tuning. Compare missed
   fists, false open palms, abstention and two-fist recognition with latency.
   Reject a speed improvement that loses the reviewed recognition performance.
8. Revert the experiment if thermal load, buffering, failure recovery or gesture
   metrics worsen. Record the accepted configuration and tested dependency versions.

Five-frame confirmation at ideal 30 fps spans about 133 ms after the first sample;
inference, camera age and transport add delay. At 5 fps it spans about 800 ms.
Changing capture rate therefore changes effective gesture confirmation latency
even if debounce stays five. Do not compensate by weakening debounce, extending
loss timeouts or lowering confidence thresholds without an explicit safety review.

The 2/5-second input-loss behavior and FC freshness bounds are control behavior,
not CPU tuning knobs. A per-frame elapsed-time gate only handles a returned call;
it cannot interrupt blocked native capture/inference. A heartbeat produced by
that same blocked callback cannot supervise itself. An independent process and
reviewed restart/latch semantics remain necessary before claiming stall coverage.

No NPU acceleration, board-specific camera driver, verified ARM dependency lock,
real exposure-age bound, thermal acceptance limit or target latency result is
provided here. Hardware-specific tuning requires evidence on the actual board.
