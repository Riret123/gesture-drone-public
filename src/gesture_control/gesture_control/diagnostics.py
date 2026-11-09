"""Read-only health report from explicit inputs; no probing or shell execution."""
from .validation import finite

COMPONENTS = ('camera', 'gesture', 'mavros', 'bridge', 'telemetry')


def diagnose(ages: dict, connected: bool, armed: bool | None,
             timeout: float = 1.) -> dict:
    if not finite(timeout) or timeout <= 0:
        raise ValueError('positive timeout required')
    if type(ages) is not dict:
        raise ValueError('component ages must be a dictionary')
    states = {}
    for name in COMPONENTS:
        age = ages.get(name)
        valid = finite(age) and 0 <= age < timeout
        states[name] = 'fresh' if valid else 'missing_or_stale'
    warnings = [name + ': missing/stale' for name, state in states.items() if state != 'fresh']
    if connected is not True:
        warnings.append('FC disconnected or unknown')
    if armed is not False:
        warnings.append('FC armed or unknown: do not assume safe bench state')
    return dict(healthy=not warnings, components=states, warnings=warnings)
