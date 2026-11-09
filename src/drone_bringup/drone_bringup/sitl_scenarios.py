"""Transport-independent acceptance scenarios; no hardware or ROS imports.

Transport methods must wait for correlated ACKs and fresh measured state.
Returning True is evidence supplied by the adapter, not inferred by this runner.
"""
SCENARIOS = ('takeoff', 'hold', 'land', 'emergency', 'rc-loss')


def plan(name):
    if name not in SCENARIOS:
        raise ValueError('unknown SITL scenario')
    steps = [('expect', 'connected_disarmed', 10.),
             ('command', 'open_palm', None),
             ('expect', 'airborne_at_target', 30.)]
    if name == 'hold':
        steps += [('command', 'hold', None), ('expect', 'loiter_stable', 10.)]
    elif name == 'rc-loss':
        steps += [('fault', 'rc_loss', None),
                  ('expect', 'configured_rc_failsafe', 15.)]
    steps += [('command', 'emergency' if name == 'emergency' else 'land', None),
              ('expect', 'landed_disarmed', 60.)]
    return tuple(steps)


def run_scenario(name, transport):
    for operation, value, timeout in plan(name):
        accepted = (transport.expect(value, timeout) if operation == 'expect'
                    else getattr(transport, operation)(value))
        if accepted is not True:
            return False, f'{operation}:{value}:FAIL; manual SITL recovery required'
    return True, 'scenario observations accepted by transport'
