from hand_tracker import HandTracker
import cv2

# TODO: Implement the volume control logic using the HandTracker class.
# 1. get the two fingertips
# 2. calculate the distance between them
# 3. map the distance to a volume level (0-100)
# 4. set the system volume to the calculated level
# 5. connecting everything together in a loop that captures frames from the webcam and processes them using the HandTracker class.
# 6. add visual feedback to the user 
# 7. add smoothing to the volume control to avoid sudden jumps in volume level.
# 8. add a simple safety activation gesture 

def main():
    hand_tracker = HandTracker()
    cap = cv2.VideoCapture(0)