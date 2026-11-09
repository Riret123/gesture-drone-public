# Orange Pi performance acceptance

There is no measured Orange Pi camera/MediaPipe/ROS result in this checkout.
The software does not configure the Rockchip NPU. CPU, GPU and NPU marketing
throughput cannot establish this pipeline's latency.

The startup requests now default to 640x480, 30 fps, model_complexity=0.
Width is bounded to 160..1920, height 120..1080, FPS 5..60 and model 0/1.
Requested capture settings may be negotiated differently by the camera driver.
Measure actual timestamps and reported properties before accepting a profile.
Increasing resolution or FPS changes processing demand and gesture sampling.
MediaPipe documents that increasing model complexity generally increases both
accuracy and latency; compare held-out errors as well as timing using the exact
installed version. [MediaPipe Hands source documentation](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md)

The new frame_budget_ms default is 200 ms, reviewed range 20..500. A callback
that returns after this budget contributes missing input, not a valid gesture.
This is a returned-processing guard, not an exposure-age bound or interrupt of
native code. The bridge separately watches completed-frame heartbeats at 3 s
default, range 0.5..10; a stopped gesture process/native stall after first health
can cause an emergency request. Both processes dead means neither can protect
the vehicle. Independent FC failsafes and pilot authority remain necessary.

Initial no-flight comparison matrix:

| Requested camera | Requested FPS | Models | Evidence required |
|---|---|---|---|
| 640x480 | 15, 30 | 0, 1 | Baseline latency/error/temperature trace |
| 320x240 | 15, 30 | 0, 1 | Confirm hand landmark quality at operating distance |
| 1280x720 | 15, 30 | 0, 1 | Accept only if image detail improves held-out errors within budget |

For one serial worker, estimate average CPU demand as completed frames/second
times CPU seconds/frame. Example arithmetic: 30 frames/s at 0.03 CPU seconds/frame
is 0.9 CPU-core equivalents before ROS/video overhead. This example is not a
board measurement. Use process CPU time for demand, monotonic time for latency;
native inference may use multiple threads. Leave measured scheduling/thermal
headroom for MAVROS and the bridge; do not pin cores or change governors by default.

With five-frame debounce, ideal confirmation adds four frame intervals after
the first sample: approximately 267 ms at 15 fps and 133 ms at 30 fps. Include
exposure, queueing, inference, ROS dispatch and observed FC transition separately.
Do not reduce debounce or increase loss timeouts to conceal an overloaded CPU.

Board commands below only observe; keep bridge stopped and motor power disconnected.
Use the actual workspace, source its environment, and keep one camera owner:

```bash
python3 -B tools/check_core_config.py
python3 -B tools/benchmark_core.py --repeats 1000
python3 -c 'import cv2, mediapipe; print(cv2.__version__, mediapipe.__version__)'
lscpu
free -h
df -h .
timedatectl show -p NTPSynchronized --value
ps -eo pid,comm,pcpu,pmem --sort=-pcpu
```

The benchmark deliberately runs only synthetic pure-Python landmark classification.
It does not open a camera or import MediaPipe/ROS. A Windows AMD64 run on
2026-11-09 measured 400 samples: total p50 0.0701 ms, p95 0.0807 ms, maximum
1.7879 ms. A recorded raw sample is checked by test_measured_core_latency.py.
These numbers establish accounting/fixture provenance only, not ARM throughput,
camera inference latency or a worst-case bound. LatencyLedger's `inference_ms`
field in this benchmark means the pure classifier interval only.

For target acceptance, capture measured exposure/dequeue uncertainty, inference
start/end, classification/publication, bridge receipt, service submit/response,
and FC-observed transition using one identified clock domain. Compare cold startup,
30-minute warm operation, low light, two hands, USB contention, video enabled
separately, thermal throttling and CPU contention. Retain p50/p95/p99/max, missed
frames, over-budget count and error labels outside source. Stop on unexpected
arming, stale health, thermal warnings, repeated deadline misses or false open palm.
No target performance acceptance threshold is claimed from the Windows fixture.
