"""Thin ROS CLI adapter; imports ROS only after explicit send request."""
from .cli_logic import parse_args


def main(args=None):
    command, send = parse_args(args)
    if not send:
        print('DRY RUN /flight_cmd: ' + command)
        return 0
    import rclpy
    from std_msgs.msg import String
    rclpy.init(args=[])
    node = rclpy.create_node('dronectl')
    try:
        publisher = node.create_publisher(String, '/flight_cmd', 10)
        # Bounded discovery; no automatic retry or takeoff repetition.
        import time
        deadline = time.monotonic() + 2.
        while publisher.get_subscription_count() == 0 and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=.1)
        if publisher.get_subscription_count() == 0:
            raise RuntimeError('No command subscriber discovered; nothing sent')
        publisher.publish(String(data=command))
        rclpy.spin_once(node, timeout_sec=.2)
        print('Published once; flight acknowledgement NOT verified')
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
