from hand_tracker import HandTracker
import cv2
import math
import numpy as np
from pycaw.pycaw import AudioUtilities

# TODO: Implement the volume control logic using the HandTracker class.
# 5. connecting everything together in a loop that captures frames from the webcam and processes them using the HandTracker class.
# 6. add visual feedback to the user
# 7. add smoothing to the volume control to avoid sudden jumps in volume level.
# 8. add a simple safety activation gesture


class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        self._volume = devices.EndpointVolume

    def get_volume(self):
        return self._volume.GetMasterVolumeLevelScalar() * 100

    def set_volume(self, volume_percentage):
        volume_level = clamp(volume_percentage, 0, 100) / 100
        self._volume.SetMasterVolumeLevelScalar(volume_level, None)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def calculate_distance(point1, point2):
    return math.hypot(point2["x"] - point1["x"], point2["y"] - point1["y"])


def distance_to_volume_percentage(distance):
    min_distance = CONTROL_MIN_DISTANCE
    max_distance = CONTROL_MAX_DISTANCE
    return clamp(np.interp(distance, [min_distance, max_distance], [0, 100]), 0, 100)


PINCH_START_THRESHOLD = 0.055
PINCH_END_THRESHOLD = 0.085
CONTROL_MIN_DISTANCE = 0.110
CONTROL_MAX_DISTANCE = 0.300
SMOOTHING_FACTOR = 0.12
VOLUME_UPDATE_THRESHOLD = 0.4
VOLUME_SETTLED_THRESHOLD = 0.1


def main():
    hand_tracker = HandTracker()
    volume_controller = VolumeController()
    cap = cv2.VideoCapture(0)

    selected_volume = volume_controller.get_volume()
    target_volume = selected_volume
    committed_volume = selected_volume
    displayed_volume = selected_volume
    pinched = False
    distance = 0.0
    is_pinching = False

    while True:
        success, frame = cap.read()
        if not success:
            break

        hand_tracker.detect(frame)
        landmarks = hand_tracker.landmarks
        distance = 0.0
        is_pinching = False

        if landmarks:
            hand = landmarks[0]
            thumb_tip = hand[4]
            index_tip = hand[8]
            distance = calculate_distance(thumb_tip, index_tip)
            if pinched:
                is_pinching = distance <= PINCH_END_THRESHOLD
            else:
                is_pinching = distance <= PINCH_START_THRESHOLD

        if not landmarks:
            pinched = False
        elif is_pinching:
            pinched = True
        elif distance >= CONTROL_MIN_DISTANCE:
            selected_volume = distance_to_volume_percentage(distance)
            target_volume = selected_volume
            pinched = False

        if abs(target_volume - committed_volume) > VOLUME_UPDATE_THRESHOLD:
            committed_volume += (target_volume - committed_volume) * SMOOTHING_FACTOR
            if abs(committed_volume - displayed_volume) >= VOLUME_UPDATE_THRESHOLD:
                volume_controller.set_volume(committed_volume)
                displayed_volume = committed_volume
        elif abs(target_volume - displayed_volume) > VOLUME_SETTLED_THRESHOLD:
            committed_volume = target_volume
            volume_controller.set_volume(committed_volume)
            displayed_volume = committed_volume

        if pinched:
            status = "SET"
        elif distance < CONTROL_MIN_DISTANCE:
            status = "HOLD"
        else:
            status = "SCROLL"
        cv2.putText(
            frame,
            status,
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Selected: {selected_volume:.0f}%",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Volume: {committed_volume:.0f}%",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        hand_tracker.draw(frame)
        cv2.imshow("Volume Controller", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
