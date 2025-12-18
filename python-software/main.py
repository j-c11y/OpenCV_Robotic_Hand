import cv2
import mediapipe as mp
import numpy as np
import serial
import time
import threading
import queue

from src.serial_worker import serial_worker
from src.angles import get_finger_angles

# ===================== Serial Setup =====================
SERIAL_PORT = "/dev/tty.usbmodem101"
BAUD_RATE = 9600
serial_queue = queue.Queue()

t = threading.Thread(target=serial_worker, args=(SERIAL_PORT, BAUD_RATE, serial_queue))
t.start()

# ===================== MediaPipe Setup =====================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ===================== Webcam =====================
cap = cv2.VideoCapture(0)


# ===================== Smoothing State =====================
SMOOTHING = 0.85
smoothed_angles = {
    "Thumb": 90,
    "Index": 90,
    "Middle": 90,
    "Ring": 90,
    "Pinky": 90,
}

# ===================== Main Loop =====================

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        current_landmarks = np.array([
            [lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark
        ])

        angles = get_finger_angles(current_landmarks)

        for finger in angles:
            smoothed_angles[finger] = (
                SMOOTHING * smoothed_angles[finger]
                + (1 - SMOOTHING) * angles[finger]["servo"]
            )

            # inside your main loop, after computing smoothed_angles
            packet = ",".join(str(int(smoothed_angles[f])) for f in ["Thumb","Index","Middle","Ring","Pinky"])
            try:
                serial_queue.put_nowait(packet)
            except queue.Full:
                pass  # skip if queue is full


        # ===== Render angles on screen =====
        y = 40
        for finger in smoothed_angles:
            text = f"{finger}: {int(smoothed_angles[finger])} deg"
            cv2.putText(
                frame,
                text,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
            y += 35

    cv2.imshow("Hand → Robot Finger Angles", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break


# ===================== Cleanup =====================
serial_queue.put("QUIT")
t.join()

cap.release()
cv2.destroyAllWindows()
