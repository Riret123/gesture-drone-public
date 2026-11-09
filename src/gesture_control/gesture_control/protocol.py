"""Strict bounded JSON envelope with CRC32; no transport or authentication."""
import json
from .validation import finite
import zlib

MAX_PACKET = 1024


def _body(seq: int, mode: str, linear: float, angular: float) -> dict:
    if type(seq) is not int or not 0 <= seq <= 2**32 - 1:
        raise ValueError('invalid sequence')
    if mode not in ('hold', 'follow', 'return_home'):
        raise ValueError('invalid mode')
    if any(not finite(v)
           for v in (linear, angular)):
        raise ValueError('invalid velocity')
    if abs(linear) > .2 or abs(angular) > 1:
        raise ValueError('velocity out of bounds')
    return dict(version=1, seq=seq, mode=mode, linear=linear, angular=angular)


def _canonical(body: dict) -> bytes:
    return json.dumps(body, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def encode(seq: int, mode: str, linear: float = 0., angular: float = 0.) -> bytes:
    body = _body(seq, mode, linear, angular)
    return _canonical(dict(body, checksum=f'{zlib.crc32(_canonical(body)):08x}'))


def decode(packet: bytes) -> dict:
    if not isinstance(packet, (bytes, bytearray)):
        raise ValueError('packet must be bytes')
    if len(packet) > MAX_PACKET:
        raise ValueError('packet too large')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    try:
        data = json.loads(packet, object_pairs_hook=unique)
        if not isinstance(data, dict) or set(data) != {
                'version', 'seq', 'mode', 'linear', 'angular', 'checksum'}:
            raise ValueError('invalid fields')
        if type(data['version']) is not int or data['version'] != 1:
            raise ValueError('unsupported version')
        body = _body(data['seq'], data['mode'], data['linear'], data['angular'])
        if data['checksum'] != f'{zlib.crc32(_canonical(body)):08x}':
            raise ValueError('checksum mismatch')
        return body
    except (TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('invalid packet') from exc
