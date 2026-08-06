
import cv2
from HandTrackingMin import HandTracker

cap = cv2.VideoCapture(0)

tracker = HandTracker()

while True:

    success, frame = cap.read()

    if not success:
        break

    tracker.detect(frame)

    tracker.draw_landmarks(frame)
    tracker.draw_connections(frame)
    #tracker.draw_ids(frame)

    landmarks = tracker.get_landmarks()

    cv2.imshow("Webcam", frame)

    # 27 stays for esc
    if cv2.waitKey(1) == 27:
        break


cap.release()
cv2.destroyAllWindows()