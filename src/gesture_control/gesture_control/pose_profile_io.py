"""Strict bounded calibration persistence; no automatic live activation."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import uuid
from .pose_features import PoseProfile


def _identity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,96}', value):
        raise ValueError('identity must contain 1..96 ASCII identifier characters')
    return value


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate profile key')
        result[key] = value
    return result


def _deployment_profile(profile):
    if (not isinstance(profile, PoseProfile) or profile.min_confidence < .5
            or profile.extended_min - profile.folded_max < 10):
        raise ValueError('deployment profile needs confidence >=0.5 and angle gap >=10 degrees')
    return profile


def load_profile(path, *, camera_id, model_id):
    """Fail closed on version/identity/schema mismatch, never load code/pickle."""
    with Path(path).open('rb') as stream:
        payload = stream.read(8193)
    if len(payload) > 8192:
        raise ValueError('profile exceeds 8192 bytes')
    try:
        data = json.loads(payload.decode('utf-8'), object_pairs_hook=_unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              ValueError('nonfinite JSON')))
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('invalid profile encoding/structure') from exc
    if (not isinstance(data, dict) or set(data) != {
            'version', 'camera_id', 'model_id', 'profile'}
            or type(data['version']) is not int or data['version'] != 1
            or data['camera_id'] != _identity(camera_id)
            or data['model_id'] != _identity(model_id)):
        raise ValueError('profile schema/version/identity mismatch')
    values = data['profile']
    if not isinstance(values, dict) or set(values) != {
            'folded_max', 'extended_min', 'min_confidence'}:
        raise ValueError('invalid profile angle schema')
    return _deployment_profile(PoseProfile(**values))


def save_profile(path, profile, *, camera_id, model_id):
    """Atomic replacement in an existing directory; stores no personal identity."""
    _deployment_profile(profile)
    data = {'version': 1, 'camera_id': _identity(camera_id),
            'model_id': _identity(model_id), 'profile': asdict(profile)}
    path = Path(path)
    temporary = None
    created = False
    try:
        temporary = path.parent / ('.profile-' + uuid.uuid4().hex + '.tmp')
        with temporary.open(mode='x', encoding='utf-8') as stream:
            created = True
            json.dump(data, stream, allow_nan=False, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if created and temporary is not None:
            temporary.unlink(missing_ok=True)
