"""Small strict numeric predicates for untrusted offline adapter inputs."""
import math


def finite(value) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def vector(value, length: int) -> bool:
    return (isinstance(value, (tuple, list)) and len(value) == length
            and all(finite(v) for v in value))
