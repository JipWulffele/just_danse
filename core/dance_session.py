import cv2
import time
import streamlit as st
from utils.utils_streamlit import wait_for_person, countdown, load_icons
from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.visualizer import Visualizer
from core.ecran import Ecran

class DanceSession:
    def __init__(self, dance_config, source=0, frame_window=None):
        self.dance_config = dance_config
        self.video = VideoHandler(source)
        self.video.set_rotation(-90)
        self.detector = PoseDetector()
        self.visualizer = Visualizer()
        self.ecran = Ecran()
        self.frame_window = frame_window

    def wait_for_person_and_countdown(self, countdown_seconds=3):
        """Run wait_for_person logic and countdown, return the latest frame."""

        detected = False

        # Loop until a person is detected
        while True:
            frame = self.video.get_frame()
            if frame is None:
                break

            results = self.detector.detect(frame)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                required = [0, 23, 24, 27, 28, 31, 32]  # nose, hips, ankles, feet
                if all(lm[i].visibility > 0.6 for i in required):
                    detected = True
                    break

                frame = self.detector.draw(frame, results)

            frame = self.visualizer.draw_warning(frame, "Please position correctly")

            # Update Streamlit window
            if self.frame_window is not None:
                self.frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Run countdown if person detected
        if detected:
            frame = countdown(self.video, seconds=countdown_seconds, frame_window=self.frame_window)
            return True, frame

        return False, frame
    

    def run_frame(self):
        frame = self.video.get_frame()
        #frame = self.visualizer.overlay_score_sticker(frame, 0)  # Placeholder
        return frame

    def is_open(self):
        return self.video.is_open()

    def release(self):
        self.video.release()