"""UNTESTED MicroPython receiver skeleton; all hardware output disabled.

Port protocol.py to the target's JSON/CRC APIs and review canonical encoding
before use. No pins, motor power, arming, serial port or radio is configured.
"""


def motor_output(left: float, right: float) -> None:
    """Replace only after unpowered driver review; currently fail closed."""
    if left != 0 or right != 0:
        raise RuntimeError('Motor driver deliberately disabled')


class Receiver:
    """Use a local monotonic millisecond tick; reset only while stopped."""

    def __init__(self, decode, ticks_diff):
        self.decode = decode
        self.ticks_diff = ticks_diff
        self.last_seq = -1
        self.last_ms = None

    def receive(self, raw: bytes, now_ms: int) -> bool:
        try:
            packet = self.decode(raw)
        except (ValueError, TypeError):
            return False
        if packet['seq'] <= self.last_seq:
            return False
        self.last_seq = packet['seq']
        self.last_ms = now_ms
        # Future adapter: map validated mode and velocities to wheel rates.
        # Remain stopped until localization, estop and driver are implemented.
        motor_output(0, 0)
        return True

    def poll(self, now_ms: int) -> None:
        if self.last_ms is None or not 0 <= self.ticks_diff(now_ms, self.last_ms) < 500:
            motor_output(0, 0)
