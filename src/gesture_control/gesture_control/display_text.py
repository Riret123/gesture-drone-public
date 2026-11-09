"""Bounded Unicode scalar text for read-only labels, not an HTML sanitizer.

No normalization or translation is performed. Caller must still use textContent
or context-appropriate escaping. Directional formatting controls are rejected to
reduce label spoofing; ordinary RU/EN letters and emoji remain valid.
"""


def bounded_text(value, minimum, maximum):
    if type(value) is not str or not minimum <= len(value) <= maximum:
        return False
    for char in value:
        code = ord(char)
        if (code < 32 or 127 <= code <= 159 or 0xD800 <= code <= 0xDFFF
                or 0x202A <= code <= 0x202E or 0x2066 <= code <= 0x2069
                or code in (0x061C, 0x200E, 0x200F)):
            return False
    return True
