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

# implement the logic to SET the volume, not just scroll it

class VolumeController:

    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        self._volume = devices.EndpointVolume

    def set_volume(self, volume_percentage):
        volume_level = volume_percentage / 100

        self._volume.SetMasterVolumeLevelScalar(
            volume_level,
            None
        )

def calculate_distance(point1, point2):
    return math.hypot(point2["x"] - point1["x"], point2["y"] - point1["y"])

def distance_to_volume_percentage(distance):
    MIN_DISTANCE=0.032
    MAX_DISTANCE=0.432
    volume = np.interp(
    distance,
    [MIN_DISTANCE, MAX_DISTANCE],
    [0, 100]
    )
    return volume


PINCH_THRESHOLD = 0.05

def main():
    hand_tracker = HandTracker()
    volume_controller = VolumeController()
    cap = cv2.VideoCapture(0)
    
    last_volume = 50
    pinched = False

    while True: 
        success, frame = cap.read()

        if not success:
            break

        hand_tracker.detect(frame)
        landmarks = hand_tracker.landmarks

        if landmarks:
            hand = landmarks[0]
            thumb_tip = hand[4]
            index_tip = hand[8]
            distance = calculate_distance(thumb_tip, index_tip)

             # Fingers are apart -> choose volume
            if distance > PINCH_THRESHOLD:
                volume = distance_to_volume_percentage(distance)
                last_volume = volume

                pinched = False

            # Fingers are pinched -> commit volume
            else:
                if not pinched:
                    volume_controller.set_volume(last_volume)
                    pinched = True

            cv2.putText(frame, f"Distance: {distance:.3f}",(20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,(255, 255, 255),2
                )

            if pinched:
                status = "SET"
            else:
                status = "ADJUSTING"
            

            
            cv2.putText(frame,status,(20, 75),cv2.FONT_HERSHEY_SIMPLEX,
                                    1,(255, 255, 255),2
                                    )
            cv2.putText(frame, f"Volume: {volume:.0f}%",(20, 110),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2
                            )
        if cv2.waitKey(1) == 27:
                break

        hand_tracker.draw(frame)

        cv2.imshow("Volume Controller", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()