from hand_tracker import HandTracker
import cv2
import math
import numpy as np

# TODO: Implement the volume control logic using the HandTracker class.
# 4. set the system volume to the calculated level
# 5. connecting everything together in a loop that captures frames from the webcam and processes them using the HandTracker class.
# 6. add visual feedback to the user 
# 7. add smoothing to the volume control to avoid sudden jumps in volume level.
# 8. add a simple safety activation gesture 

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


def main():
    hand_tracker = HandTracker()
    cap = cv2.VideoCapture(0)

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
            volume = distance_to_volume_percentage(distance)
            cv2.putText(frame, f"Distance: {distance:.3f}",(20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,(255, 255, 255),2
                )
            cv2.putText(frame, f"Volume: {volume:.0f}%",(20, 90),
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