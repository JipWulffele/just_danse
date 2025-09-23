import mediapipe as mp
import cv2

class PoseDetector():
    def __init__(self, detection_conf=0.5, tracking_conf=0.5):
        self.mp_pose = mp.solutions.pose # https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?authuser=1&hl=fr
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf
        )
        self.drawing = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert to rgb for mediapipe
        results = self.pose.process(rgb)
        return results

    def draw(self, frame, results):
        if results.pose_landmarks:
            self.drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame