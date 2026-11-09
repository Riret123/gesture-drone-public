"""Offline battery hysteresis; cell voltage must be measured/configured correctly."""
from .validation import finite


class BatteryPolicy:
    """Critical -> land, low -> RTL, invalid -> hold; explicit recovery hysteresis.

    Prototype 3.5/3.3 V per-cell thresholds, 0.15 V recovery margin. Not a
    chemistry-independent recommendation. No automatic FC parameter changes.
    """

    def __init__(self, low: float = 3.5, critical: float = 3.3,
                 hysteresis: float = .15):
        if (not all(finite(v) for v in (low, critical, hysteresis))
                or not 0 < critical < low or hysteresis <= 0):
            raise ValueError('invalid voltage thresholds')
        if (not finite(low + hysteresis) or not finite(critical + hysteresis)
                or low + hysteresis <= low or critical + hysteresis <= critical):
            raise ValueError('recovery margin must be finite and representable')
        self.low, self.critical, self.margin = low, critical, hysteresis
        self.state = 'normal'

    def update(self, voltage: float, cells: int) -> str:
        if (type(cells) is not int or cells <= 0 or not finite(cells) or not finite(voltage)
                or voltage <= 0):
            return 'hold'
        value = voltage / cells
        if not finite(value) or value <= 0:
            return 'hold'
        if value <= self.critical:
            self.state = 'critical'
        elif self.state == 'critical' and value < self.critical + self.margin:
            pass
        elif value <= self.low:
            self.state = 'low'
        elif self.state in ('low', 'critical') and value < self.low + self.margin:
            self.state = 'low'
        else:
            self.state = 'normal'
        return {'normal': 'allow', 'low': 'rtl', 'critical': 'land'}[self.state]
