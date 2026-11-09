# Gesture reliability and latency campaign

The live classifier still uses 2D fingertip/palm ratios (default 1.1), now rejects
invalid/collapsed landmarks, and has startup ROS configuration in config/core.yaml.
Model detection/tracking confidence settings are MediaPipe thresholds, not a
calibrated gesture-confidence probability. Debounce remains five frames; missing
confirmed input holds at 2 s and lands at 5 s. Large sampling gaps reset debounce.
These behaviors and the new FC state guard require SITL validation.

pose_features.py is an **opt-in experimental** classifier using PIP and DIP angles for
four fingers, rejecting ambiguous mixtures and degenerate 3D geometry. Reflection
and rigid rotation preserve angles in synthetic fixtures, which addresses the
mathematical front/back dependence but does not establish reliable back-of-hand
recognition from MediaPipe. Occlusion can produce plausible yet incorrect model
landmarks. Use consistent metric/world coordinates; normalized image x/y and model
z do not automatically share scale. Thumb articulation is not measured here.

Proposed experiment defaults: folded joint angles <=110 degrees, extended >=160,
minimum margin score .5. The score measures distance from a threshold and is not
a probability. Per-user calibrate() requires at least five labeled samples in each
class, rejects overlapping envelopes and builds a conservative profile. Repeated
copies passing a unit test do not constitute a calibration dataset. Default empty
pose_profile_path preserves 2D classification. An explicitly configured profile
now selects world-landmark classification in the live node. There is no 2D
fallback if world outputs are unavailable or hand counts disagree. Detection and
tracking thresholds remain model settings, not gesture-confidence probabilities.

Persist profiles as bounded version-1 JSON, never pickle. Deployment persistence
requires confidence margin >=.5 and angle separation >=10 degrees; duplicate keys,
nonfinite values, wrong schema/version/camera/model or oversized files reject.
For camera 0 at 640x480/30 fps with the node's mirror setting, camera identity is
`camera-0-640x480-30fps-mirror1`. Model identity is
`mediapipe:VERSION:hands-world:model0`; replace VERSION with the exact installed
`mediapipe.__version__`. Model 1 has a distinct identity. Negotiated dimensions
must match; reported FPS must be within 10 percent. Identity strings do not prove
physical sensor identity or model authenticity; camera index reassignment remains
an acceptance risk.

Offline calibration requires independently labeled metric/world CSV files, each
with at least five one-hand frames and the header `time,hand,index,x,y,z`; each
hand has indexes 0..20. Never use normalized image coordinates as metric world
coordinates. CLI calibration rejects fewer than five distinct poses per class,
including frozen/replayed copies. Distinct coordinates still do not prove
independent exposure or adequate orientation coverage. Example command (output
directory must already exist):

For human camera-only collection on the board, stop bridge/gesture/video, keep
motor power disconnected, and use a consented one-hand session. These commands
are examples for the human; this agent never executed capture. The default
invocation prints a plan without importing camera libraries; --capture opens
the exclusive camera. No images/ROS/FC commands are stored or sent:

```bash
mkdir -p ~/drone_capture
python3 -B tools/capture_world.py --label open_palm --output ~/drone_capture/open_world.csv
flock -n "${XDG_RUNTIME_DIR:?}/drone-camera.lock" python3 -B tools/capture_world.py \
  --capture --label open_palm --output ~/drone_capture/open_world.csv --frames 30
flock -n "${XDG_RUNTIME_DIR:?}/drone-camera.lock" python3 -B tools/capture_world.py \
  --capture --label fist --output ~/drone_capture/fist_world.csv --frames 30
```

The recorder refuses output inside the checkout, existing files, mismatched
negotiated settings, repeated exact poses, slow frames and insufficient samples.
Vary orientation/position while preserving the labeled gesture; independently
review labels and hold out separate sessions. It prints camera/model identity
and aggregate capture counts, not landmarks. Timestamps are inference completion,
not exposure. A blocked native camera call is not interrupted by its loop timeout;
this camera-only recorder must not share flight control. If interrupted during
disk writing, discard any partial external output. Stop on ownership conflict,
missing world coordinates, false labels or unexplained stalls. Calibrate only
after both files are complete, using the printed identities:

```bash
python3 -B tools/calibrate_pose.py --open ~/drone_capture/open_world.csv \
  --fist ~/drone_capture/fist_world.csv \
  --coordinates world --camera-id camera-0-640x480-30fps-mirror1 \
  --model-id mediapipe:VERSION:hands-world:model0 --output ~/drone_capture/USER_PROFILE.json
```

Keep user recordings/profiles outside source and redact personal data. Do held-out
orientation/occlusion tests with the bridge stopped before setting pose_profile_path
to a double-quoted local path in a copy of config/core.yaml. Validate with
tools/check_core_config.py. A profile that passes the schema is not flight approval.
The calibration CLI refuses output inside source and requires --replace-profile
for an existing destination. Use an absolute profile path in YAML; shell tilde
expansion does not occur inside a quoted parameter-file string.

The standalone gesture_test.py preview remains the default 2D classifier; it does
not validate an activated 3D profile, frame-budget gate or ROS timing. Observe the
actual gesture_node with its reviewed params and every control bridge stopped
when validating the optional live profile. Over-budget two-fist results are stale
input and abstain: repeated slow frames still advance the 2/5-second input-loss
hold/land path, rather than renewing the lease or promising immediate emergency.

Collect consented no-flight sessions with bridge stopped: palm and back of hand,
both hands, roll/pitch/yaw rotation, partial occlusion, thumb variants, side-on,
different camera distances, blur, low light, glare, gloves, clutter, hands absent,
two conflicting hands and two fists. Include multiple users and hold out whole
sessions/users. Record camera geometry, model version and world-coordinate
availability. Label from independent image review; exclude personal imagery from
source control. Report false open-palm events per hour, false emergency/landing,
missed fist, abstention rate, time-to-confirm and recovery after camera loss.
No quantitative camera accuracy claim is available yet.

Latency measurement boundaries use one monotonic clock: true exposure/capture,
inference start/end, policy decision/publication, bridge receipt, request submit,
service response and FC-observed transition. Timestamping cap.read() return is
dequeue time, not exposure; include buffer uncertainty. A 30 Hz timer does not
guarantee 30 Hz inference. Five-frame confirmation adds at least four interframe
intervals (~133 ms at ideal 30 Hz) after the first sample, plus image age and
transport/FC delay. Native camera calls can block the timer indefinitely.

Provisional measurement targets (not validated limits): camera age <=50 ms,
inference <=30 ms, policy/publication <=10 ms, ROS dispatch <=10 ms; 100 ms from
capture to dispatch excludes deliberate debounce and FC response. Collect under
CPU/thermal contention, camera reconnect and low light; report distributions,
worst observed case and timestamp uncertainty. core_latency.LatencyLedger provides
bounded nearest-rank p50/p95/max summaries and budget exceedance totals. It is not
wired to ROS, cannot measure true exposure, and never changes commands. A measured
maximum is not a proven worst-case bound.

Do not reduce debounce, increase loss timeouts or lower gesture-confidence gates
to improve a demo without explicitly reviewing the resulting flight behavior.
