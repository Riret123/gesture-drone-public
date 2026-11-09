"""Canonical legacy command/ACK framing; no authentication or request identity."""
COMMANDS = frozenset(('open_palm', 'fist', 'land', 'emergency', 'hold', 'other',
                      'operator_reset'))


def canonical_command(value):
    return value if isinstance(value, str) and len(value) <= 32 and value in COMMANDS else None


def acknowledgement(command, ok, detail):
    if canonical_command(command) is None:
        return 'invalid:FAIL:unsupported command'
    if type(ok) is not bool or not isinstance(detail, str):
        return f'{command}:FAIL:invalid internal result'
    # One logical ACK record. Never echo controls/newlines or an unbounded error.
    detail = ''.join(char if char.isprintable() else ' ' for char in detail[:384])
    return f'{command}:{"OK" if ok else "FAIL"}:{detail}'
