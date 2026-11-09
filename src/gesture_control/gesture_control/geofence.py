"""Advisory local-home geofence, never a replacement for FC failsafes."""
import math
from .validation import finite


def evaluate(x: float, y: float, altitude: float, battery: float,
             radius: float = 20., ceiling: float = 5.,
             rtl_percent: float = 25.) -> str:
    """Return hold on invalid telemetry, RTL on boundary or low battery.

    Home is (0, 0); height is relative to home; boundary is inclusive.
    RTL availability/home validity must be checked by a future adapter.
    """
    if not all(finite(v) for v in (radius, ceiling, rtl_percent)):
        raise ValueError('invalid configuration')
    if radius <= 0 or ceiling <= 0 or not 0 < rtl_percent < 100:
        raise ValueError('invalid configuration')
    if (not all(finite(v) for v in (x, y, altitude, battery))
            or altitude < 0 or not 0 <= battery <= 100):
        return 'hold'
    if math.hypot(x, y) >= radius or altitude >= ceiling or battery <= rtl_percent:
        return 'rtl'
    return 'allow'
