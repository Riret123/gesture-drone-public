"""Strict versioned offline settings; never loads or alters FC parameters."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class OfflineConfig:
    version: int = 1
    rover_timeout: float = .5
    telemetry_timeout: float = 1.
    wheel_track: float = .3
    wheel_speed: float = .4

    @classmethod
    def from_dict(cls, data: dict):
        fields = {'version', 'rover_timeout', 'telemetry_timeout', 'wheel_track', 'wheel_speed'}
        if not isinstance(data, dict) or set(data) - fields:
            raise ValueError('unknown configuration keys')
        result = cls(**data)
        if type(result.version) is not int or result.version != 1:
            raise ValueError('unsupported configuration version')
        for name in fields - {'version'}:
            value = getattr(result, name)
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('finite positive settings required')
        if result.rover_timeout > 1 or result.telemetry_timeout > 5:
            raise ValueError('offline watchdog exceeds allowed experimental bound')
        if result.wheel_speed > .4 or result.wheel_track > 2:
            raise ValueError('offline rover geometry/speed exceeds experimental bound')
        return result
