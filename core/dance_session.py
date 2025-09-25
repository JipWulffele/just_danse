import cv2
import time
import streamlit as st
import numpy as np

from utils.utils_streamlit import countdown, load_icons

from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.visualizer import Visualizer
from core.ecran import Ecran
from core.dance_judge import DanceJudge
from core.audio_player import AudioSyncPlayer

class DanceSession:
    def __init__(self, dance_config, sticker_config, icon_data=None, source=0, frame_window=None):
        self.dance_config = dance_config
        self.sticker_config = sticker_config
        self.icon_data = icon_data
        
        self.video = VideoHandler(source)
        self.video.set_rotation(-90)
        
        self.detector = PoseDetector()

        data = np.load(dance_config["ref_keypoints"])
        ref_keypoints_seq = data["keypoints"]
        self.judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20], angle_deg=dance_config["webcam_rotation"])
        
        self.visualizer = Visualizer()
        self.ecran = Ecran()
        
        self.frame_window = frame_window

        self.ref_video = VideoHandler(dance_config["ref_video"])
        self.ref_video.set_rotation(-90)
        self.ref_video.set_target_size(width=1080, height=720)
        self.audio_player = AudioSyncPlayer(dance_config["audio"])
        self.fps = 30 # very important!!! should match ref video or music will be out of sync
        self.frame_duration = 1.0 / self.fps


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
    
    def dance_loop(self):
        """Play reference video and show webcam feed."""
        
        # extract sticker info
        last_sticker_time = self.sticker_config["last_sticker_time"]
        sticker_start_time = self.sticker_config["sticker_start_time"]
        sticker_interval = self.sticker_config["sticker_interval"]
        sticker_duration = self.sticker_config["sticker_duration"]
        current_sticker_score = self.sticker_config["current_sticker_score"]

        # set frame rate regulation
        expected_idx = 0
        ref_frame_idx = 0
        last_ref_frame = self.ref_video.get_frame()

        self.audio_player.play()
        start_time = time.time()

        while self.ref_video.is_open():

            loop_start = time.time() # keep track of time
            elapsed = time.time() - start_time # total elapsed time
            expected_idx = int(elapsed / self.frame_duration)
            
            if expected_idx > ref_frame_idx:
                # Advance as many frames as needed
                while ref_frame_idx < expected_idx:
                    ref_frame = self.ref_video.get_frame()
                    ref_frame_idx += 1
                    if ref_frame is None:
                        break
                last_ref_frame = ref_frame
            else:
                ref_frame = last_ref_frame

            #ref_frame = self.ref_video.get_frame()
            cam_frame = self.video.get_frame()

            if ref_frame is None or cam_frame is None:
                break

            # Detection and judging
            results = self.detector.detect(cam_frame)
            if results.pose_landmarks:
                score, stage = self.judge.update(results.pose_landmarks.landmark, expected_idx=expected_idx, method="distance") # prend expected_idx
                cam_frame = self.detector.draw(cam_frame, results)

            # PiP webcam
            ref_frame = self.visualizer.overlay_pip(ref_frame, cam_frame, size=(300,200))

            # Overlay icons
            for icon_cfg in self.icon_data["icons"]:
                if icon_cfg["start_frame"] <= ref_frame_idx <= icon_cfg["end_frame"]:
                    ref_frame = self.visualizer.overlay_icon(
                        ref_frame, icon_cfg["image"], size=tuple(icon_cfg["size"])
                    )


            # Check if it's time to show a new sticker
            if elapsed - last_sticker_time >= sticker_interval:
                show_sticker = True
                last_sticker_time = elapsed  # reset last shown time
                sticker_start_time = elapsed # when we started showing this sticker
                current_sticker_score = self.judge.score
                print(f"Raw score (for debugging): {self.judge.score}")
            else:
                show_sticker = False

            # Keep showing sticker for sticker_duration
            if current_sticker_score and (show_sticker or (elapsed - sticker_start_time <= sticker_duration)):
                ref_frame = self.visualizer.overlay_score_sticker(ref_frame, current_sticker_score)

            # Display frame
            self.frame_window.image(cv2.cvtColor(ref_frame, cv2.COLOR_BGR2RGB))

        self.audio_player.stop()
        self.ref_video.release()

    def run_frame(self):
        frame = self.video.get_frame()
        return frame

    def is_open(self):
        return self.video.is_open()

    def release(self):
        self.audio_player.stop()
        self.video.release()