"""Rigid position transform helper; requires measured right-handed extrinsics."""
import math


def transform(point: tuple, rotation: tuple, translation: tuple) -> tuple:
    """p_body = R_body_camera @ p_camera + t_body_camera; SI meters.

    This transforms a position, not velocity. Validate calibration independently.
    A downward camera convention cannot be inferred from a tag detector alone.
    """
    if (len(point) != 3 or len(translation) != 3 or len(rotation) != 3
            or any(len(row) != 3 for row in rotation)):
        raise ValueError('3D transform dimensions required')
    values = [*point, *translation, *(v for row in rotation for v in row)]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('finite transform required')
    for i in range(3):
        for j in range(3):
            dot = sum(rotation[i][k] * rotation[j][k] for k in range(3))
            if abs(dot - (1 if i == j else 0)) > 1e-6:
                raise ValueError('rotation must be orthonormal')
    a, b, c = rotation
    determinant = (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
                   + a[2]*(b[0]*c[1]-b[1]*c[0]))
    if abs(determinant - 1) > 1e-6:
        raise ValueError('reflection is not a rotation')
    return tuple(sum(rotation[i][j]*point[j] for j in range(3)) + translation[i]
                 for i in range(3))
