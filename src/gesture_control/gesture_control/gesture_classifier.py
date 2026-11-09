"""Basic 2D fingertip-to-palm ratio heuristic for 21 MediaPipe landmarks.

Front/back occlusion and inferred landmark errors remain unvalidated. Invalid
geometry abstains. See pose_features for a separate, opt-in 3D experiment.
"""

import math

# Точки, задающие центр ладони: запястье + основания (MCP) всех четырёх
# пальцев кроме большого.
PALM_POINTS = (0, 5, 9, 13, 17)

# Пары (кончик, основание/MCP этого же пальца) для всех пяти пальцев.
FINGER_TIP_MCP = [
    (4, 2),    # большой: TIP, MCP
    (8, 5),    # указательный
    (12, 9),   # средний
    (16, 13),  # безымянный
    (20, 17),  # мизинец
]

# Палец считается разогнутым, если кончик дальше от центра ладони, чем
# основание пальца, минимум в это число раз.
CURL_RATIO_THRESHOLD = 1.1

GESTURE_FIST = 'fist'
GESTURE_OPEN_PALM = 'open_palm'
GESTURE_OTHER = 'other'


def classify_gesture(landmarks, curl_ratio=CURL_RATIO_THRESHOLD):
    """landmarks — список из 21 точки с атрибутами .x/.y (нормализованные
    координаты кадра, как у hand_landmarks.landmark из MediaPipe Hands).

    Возвращает одну из GESTURE_FIST / GESTURE_OPEN_PALM / GESTURE_OTHER.
    """
    try:
        valid_ratio = (not isinstance(curl_ratio, bool)
                       and isinstance(curl_ratio, (int, float))
                       and math.isfinite(curl_ratio) and 1 < curl_ratio <= 3)
    except OverflowError:
        valid_ratio = False
    if not valid_ratio:
        raise ValueError('curl_ratio must be finite and in (1, 3]')
    # Invalid geometry must never synthesize a landing or takeoff gesture.
    try:
        if len(landmarks) != 21:
            return GESTURE_OTHER
        coordinates = [(point.x, point.y) for point in landmarks]
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) or abs(v) > 10
               for point in coordinates for v in point):
            return GESTURE_OTHER
    except (TypeError, AttributeError, OverflowError):
        return GESTURE_OTHER
    cx = sum(coordinates[i][0] for i in PALM_POINTS) / len(PALM_POINTS)
    cy = sum(coordinates[i][1] for i in PALM_POINTS) / len(PALM_POINTS)

    def dist_to_center(idx):
        return math.hypot(coordinates[idx][0] - cx, coordinates[idx][1] - cy)

    if max(dist_to_center(i) for i in PALM_POINTS) <= 1e-9:
        return GESTURE_OTHER
    fingers_extended = sum(
        dist_to_center(tip) > dist_to_center(mcp) * curl_ratio
        for tip, mcp in FINGER_TIP_MCP)
    if fingers_extended == 0:
        return GESTURE_FIST
    if fingers_extended >= 4:
        return GESTURE_OPEN_PALM
    return GESTURE_OTHER
