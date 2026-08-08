import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

class HandTracker:

    def __init__(self, model_path='models/hand_landmarker.task', _num_hands=1):
        self.base_options = python.BaseOptions(model_asset_path=model_path)
        self.options = vision.HandLandmarkerOptions(base_options=self.base_options, running_mode=vision.RunningMode.VIDEO, num_hands=_num_hands)
        self._detector = vision.HandLandmarker.create_from_options(self.options)
        self._HAND_CONNECTIONS = [
            (0,1),(1,2),(2,3),(3,4),
            (0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),
            (9,13),(13,14),(14,15),(15,16),
            (13,17),(17,18),(18,19),(19,20),
            (0,17)
            ]
        self._timestamp_ms = 0
        self._result = None
        self._landmarks = []

    @property
    def timestamp_ms(self):
        return self._timestamp_ms

    @property
    def result(self):
        return self._result

    @property
    def hand_connections(self):
        return tuple(self._HAND_CONNECTIONS)

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._timestamp_ms = int(time.time() * 1000)
        self._result = self._detector.detect_for_video(mp_image, self._timestamp_ms)
        self._landmarks = self._extract_landmarks()


    def _extract_landmarks(self):

        landmarks = []
        if self._result is None:
            return landmarks

        for hand in self._result.hand_landmarks:
            hand_landmarks = []
            for id, lm in enumerate(hand):
                hand_landmarks.append({
                    "id": id,
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z
                })
            landmarks.append(hand_landmarks)
        return landmarks

    def draw_landmarks(self, frame):
        if self._result is None:
            return frame
        height, width, _ = frame.shape

        for hand in self._result.hand_landmarks:
                    for landmark in hand:
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
        
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)


    def draw_connections(self, frame):
        if self._result is None:
                    return frame
        height, width, _ = frame.shape
        
        for hand in self._result.hand_landmarks:
            for start, end in self._HAND_CONNECTIONS:
                x1 = int(hand[start].x * width)
                y1 = int(hand[start].y * height)

                x2 = int(hand[end].x * width)
                y2 = int(hand[end].y * height)

                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)


    def draw_ids(self, frame):
        if self._result is None:
                            return frame
        height, width, _ = frame.shape
        
        for hand in self._result.hand_landmarks:
            for id, landmark in enumerate(hand):
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                cv2.putText(frame, str(id), (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    def draw(self, frame):
        height, width, _ = frame.shape

        if self._result is None:
            return frame

        for hand in self._result.hand_landmarks:
            for id, landmark in enumerate(hand):
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(frame, str(id), (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        for hand in self._result.hand_landmarks:
            for start, end in self._HAND_CONNECTIONS:
                x1 = int(hand[start].x * width)
                y1 = int(hand[start].y * height)

                x2 = int(hand[end].x * width)
                y2 = int(hand[end].y * height)

                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        return frame


    @property
    def landmarks(self):
        return tuple(self._landmarks)