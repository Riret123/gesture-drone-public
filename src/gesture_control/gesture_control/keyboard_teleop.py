"""Interactive Linux terminal adapter. No background keyboard capture."""
import select
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from gesture_control.teleop_logic import command_for_key


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher = self.create_publisher(String, '/flight_cmd', 10)
        self.timer = self.create_timer(0.05, self.poll)

    def poll(self):
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key in ('q', '\x03', ''):
                rclpy.shutdown()
                return
            command = command_for_key(key)
            if command:
                self.publisher.publish(String(data=command))


def main(args=None):
    if not sys.stdin.isatty():
        raise RuntimeError('keyboard_teleop requires an interactive terminal')
    previous = termios.tcgetattr(sys.stdin)
    node = None
    rclpy.init(args=args)
    try:
        tty.setcbreak(sys.stdin.fileno())
        node = KeyboardTeleop()
        print('t: TAKEOFF 2m; l: land; h: LOITER hold; SPACE: emergency land; q: quit')
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous)
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
