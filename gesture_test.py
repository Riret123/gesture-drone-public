#!/usr/bin/env python3
"""
Тест распознавания базовых жестов руки через веб-камеру.
Камера -> MediaPipe Hands -> скелет на видео + название жеста в консоль.

Запуск:
    source ai_env/bin/activate
    python gesture_test.py
Выход: клавиша 'q' или Esc.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src/gesture_control'))
from gesture_control.gesture_classifier import classify_gesture

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release()
        print('Camera unavailable (index 0)')
        return

    try:
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
            max_num_hands=2,
        ) as hands:
            last_printed = None
            while True:
                ok, frame = cap.read()
                if not ok:
                    print("Кадр не получен, завершение")
                    break

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb.flags.writeable = False
                results = hands.process(rgb)

                gesture_text = "рука не найдена"

                if results.multi_hand_landmarks:
                    gestures = []
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style(),
                        )
                        gesture = classify_gesture(hand_landmarks.landmark)
                        gestures.append(gesture)

                        h, w, _ = frame.shape
                        wrist = hand_landmarks.landmark[0]
                        cv2.putText(
                            frame,
                            gesture,
                            (int(wrist.x * w), int(wrist.y * h) + 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                        )
                    gesture_text = ", ".join(gestures)

                if gesture_text != last_printed:
                    print(f"Жест: {gesture_text}")
                    last_printed = gesture_text

                cv2.imshow("gesture_test (q/Esc — выход)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break

    finally:
        try:
            cap.release()
        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
