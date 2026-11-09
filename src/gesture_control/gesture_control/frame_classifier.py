"""Shared frame classification for camera and deterministic replay adapters."""
from .gesture_classifier import classify_gesture
from .pose_features import classify_pose


def classify_frame(image_hands, curl_ratio=1.1, *, world_hands=None, profile=None):
    """Use metric world coordinates only when an explicit profile is supplied.

    Missing/mismatched world outputs abstain; no projection-based fallback when
    the calibrated classifier was requested. At most two hands are supported.
    """
    if not isinstance(image_hands, (list, tuple)) or len(image_hands) > 2:
        return []
    if profile is None:
        return [classify_gesture(points, curl_ratio) for points in image_hands]
    if (not isinstance(world_hands, (list, tuple))
            or len(world_hands) != len(image_hands)):
        return []
    return [classify_pose(points, profile).gesture for points in world_hands]
