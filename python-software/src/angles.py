import numpy as np


"""Returns the angle at point b (in degrees) given three 3D points."""
def angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))



"""Maps MediaPipe joint angle to servo angle."""
def map_angle(val, in_min=60, in_max=170, out_min=0, out_max=180):
    return int(
        np.clip(
            (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min,
            out_min, out_max
        )
    )

"""
landmarks: np.array shape (21, 3)
returns: dict of raw + servo angles
"""
def get_finger_angles(landmarks):
    fingers = {
        "Thumb":  (1, 2, 3),
        "Index":  (5, 6, 7),
        "Middle": (9, 10, 11),
        "Ring":   (13, 14, 15),
        "Pinky":  (17, 18, 19),
    }

    results = {}
    for name, (a, b, c) in fingers.items():
        raw = angle(landmarks[a], landmarks[b], landmarks[c])
        servo = map_angle(raw)
        results[name] = {"raw": raw, "servo": servo}

    return results