#!/usr/bin/env bash
# Manual user service lifecycle. Never enables services or configures networking.
set -euo pipefail
action=${1:-help}
component=${2:-}
case "$action" in
  start|stop)
    case "$component" in mavros|gesture|bridge|camera) ;; *) echo 'Choose mavros, gesture, bridge or camera' >&2; exit 2;; esac
    systemctl --user "$action" "drone-core@${component}.service"
    ;;
  healthcheck)
    for name in mavros gesture bridge camera; do
      systemctl --user is-active "drone-core@${name}.service" || true
    done
    # Process liveness is not flight health; these observations have bounded waits.
    timeout 8 ros2 topic echo /mavros/state --once
    timeout 8 ros2 topic info /flight_cmd --verbose
    timeout 8 ros2 service list
    ;;
  collect)
    destination=${2:?provide a new local output directory}
    mkdir -m 700 -- "$destination"
    for name in mavros gesture bridge camera; do
      journalctl --user -u "drone-core@${name}.service" --since '-30 minutes' \
        --no-pager > "$destination/${name}.log"
    done
    echo 'Review logs locally for private data before sharing.'
    ;;
  run)
    : "${DRONE_WORKSPACE:?set absolute deployment workspace}"
    [[ "$DRONE_WORKSPACE" = /* ]] || { echo 'Workspace must be absolute' >&2; exit 2; }
    case "$component" in
      mavros|gesture|bridge) : "${DRONE_FCU_URL:?set verified FCU endpoint}" ;;
      camera) ;;
      *) echo 'Unknown component: choose mavros, gesture, bridge or camera' >&2; exit 2 ;;
    esac
    for required in /opt/ros/jazzy/setup.bash \
      "$DRONE_WORKSPACE/ai_env/bin/activate" "$DRONE_WORKSPACE/install/setup.bash"; do
      [[ -r "$required" ]] || { echo "Required environment file missing or unreadable: $required" >&2; exit 2; }
    done
    # Vendor environment scripts may reference unset optional shell variables.
    set +u
    source /opt/ros/jazzy/setup.bash
    source "$DRONE_WORKSPACE/ai_env/bin/activate"
    source "$DRONE_WORKSPACE/install/setup.bash"
    set -u
    cd "$DRONE_WORKSPACE"
    params="$DRONE_WORKSPACE/config/core.yaml"
    case "$component" in
      mavros)
        exec ros2 launch drone_bringup mavros_apm.launch.py "fcu_url:=$DRONE_FCU_URL" gcs_url:=
        ;;
      gesture|bridge)
        # Local endpoint attestation is insufficient alone: physically isolate FCs.
        [[ "${DRONE_MODE:-observe}" = sitl && "$DRONE_FCU_URL" = 'udp://:14550@' ]] || {
          echo 'Control nodes are restricted to isolated SITL by this template' >&2; exit 2;
        }
        python3 tools/check_core_config.py "$params"
        if [[ "$component" = gesture ]]; then
          exec flock -n "${XDG_RUNTIME_DIR:?}/drone-camera.lock" \
            ros2 run gesture_control gesture_node --ros-args --params-file "$params"
        fi
        exec ros2 run drone_bringup flight_cmd_bridge --ros-args --params-file "$params"
        ;;
      camera)
        exec flock -n "${XDG_RUNTIME_DIR:?}/drone-camera.lock" \
          python3 video_stream_server.py --host 127.0.0.1 --port 8080 --camera 0
        ;;
      *) echo 'Unknown component' >&2; exit 2;;
    esac
    ;;
  *) echo 'Usage: core.sh start|stop COMPONENT; healthcheck; collect NEW_DIRECTORY; run COMPONENT'; exit 2;;
esac
