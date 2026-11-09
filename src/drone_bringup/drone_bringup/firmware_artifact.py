"""Read-only bounded APJ inspection. Never flashes or identifies physical PCBs."""
import base64
import binascii
import hashlib
import json
import zlib

MAX_APJ_BYTES = 16 * 1024 * 1024
MAX_IMAGE_BYTES = 4 * 1024 * 1024


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('nonfinite JSON constant')


def inspect_apj(data, expected_board_id, expected_sha256=None,
                max_image_bytes=MAX_IMAGE_BYTES):
    if (type(expected_board_id) is not int or not 1 <= expected_board_id <= 65535
            or type(max_image_bytes) is not int or not 1 <= max_image_bytes <= MAX_IMAGE_BYTES):
        raise ValueError('explicit bounded integer identity/size required')
    if not isinstance(data, bytes) or not 1 <= len(data) <= MAX_APJ_BYTES:
        raise ValueError('APJ must be bounded nonempty bytes')
    artifact_hash = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None:
        if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
                or any(c not in '0123456789abcdefABCDEF' for c in expected_sha256)
                or artifact_hash != expected_sha256.lower()):
            raise ValueError('artifact SHA256 mismatch or malformed expected hash')
    try:
        doc = json.loads(data.decode('utf-8'), object_pairs_hook=_pairs,
                         parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('invalid APJ JSON') from exc
    if (not isinstance(doc, dict) or doc.get('magic') != 'APJFWv1'
            or type(doc.get('board_id')) is not int
            or doc['board_id'] != expected_board_id
            or type(doc.get('board_revision')) is not int or doc['board_revision'] < 0
            or type(doc.get('image_size')) is not int
            or not 1 <= doc['image_size'] <= max_image_bytes
            or not isinstance(doc.get('image'), str)):
        raise ValueError('APJ identity, size or required field rejected')
    try:
        compressed = base64.b64decode(doc['image'], validate=True)
        decoder = zlib.decompressobj()
        image = decoder.decompress(compressed, max_image_bytes + 1)
        if (len(image) > max_image_bytes or not decoder.eof or decoder.unconsumed_tail
                or decoder.unused_data or len(image) != doc['image_size']):
            raise ValueError('compressed image truncated, trailing, oversized or size mismatch')
    except (binascii.Error, zlib.error, UnicodeError) as exc:
        raise ValueError('invalid APJ image encoding') from exc
    return {'board_id': doc['board_id'], 'board_revision': doc['board_revision'],
            'image_size': len(image), 'artifact_sha256': artifact_hash,
            'image_sha256': hashlib.sha256(image).hexdigest(), 'signature_verified': False,
            'physical_board_verified': False}
