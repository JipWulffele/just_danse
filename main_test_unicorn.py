import json
import time
import cv2
import numpy as np

from utils.utils import wait_for_person, countdown, load_icons
from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.dance_judge import DanceJudge
from core.visualizer import Visualizer
from core.audio_player import AudioSyncPlayer
from core.ecran import Ecran

# Hyper parameters
SOURCE = 0 # webcam index
METHOD = "distance"
REF_VIDEO = "assets/video/reference_unicorn.webm"
REF_KEYPOINTS = "assets/keypoints/keypoints_reference_unicorn.npz"
ICON_PATH = "assets/config/icon_schedule.json"
AUDIO_PATH = "assets/audio/de_kabouter_dans_short.mp3"
FRAME_WIDTH = 1080
FRAME_HEIGHT = 720
WEBCAM_ROTATION = -90
FORCE_FPS = 0

# 🔹 New flag
SAVE_KEYPOINTS = True   # set False if you don't want to save


def main():

    ecran = Ecran()
    video = VideoHandler(source=SOURCE)
    video.set_rotation(WEBCAM_ROTATION)
    video.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    reference = VideoHandler(source=REF_VIDEO)
    reference.set_rotation(WEBCAM_ROTATION)
    reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    audio_player = AudioSyncPlayer(AUDIO_PATH)
    detector = PoseDetector()

    data = np.load(REF_KEYPOINTS)
    ref_keypoints_seq = data["keypoints"]
    judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20], angle_deg=WEBCAM_ROTATION)
    visualizer = Visualizer()
    icon_data = load_icons(ICON_PATH)

    if SAVE_KEYPOINTS:
        # 🔹 Storage for user keypoints
        user_keypoints_seq = []

    # Show starting screen
    start_screen_frame = ecran.get_ecran_start(size=(FRAME_WIDTH , FRAME_HEIGHT))
    ecran.show_ecran(video, reference, start_screen_frame, 2)

    while True:
        if not wait_for_person(video, detector, visualizer):
            video.release()
            return

        countdown(video, 3)

        if FORCE_FPS == 0:
            ref_fps = reference.cap.get(cv2.CAP_PROP_FPS)
        else:
            ref_fps = FORCE_FPS
        frame_duration = 1.0 / ref_fps
        ref_frame_idx = 0
        last_ref_frame = None

        audio_player.play()
        start_time = time.time()

        while video.is_open():
            loop_start = time.time()
            elapsed = time.time() - start_time
            expected_idx = int(elapsed / frame_duration)

            if expected_idx > ref_frame_idx:
                while ref_frame_idx < expected_idx:
                    ref_frame = reference.get_frame()
                    ref_frame_idx += 1
                    if ref_frame is None:
                        break
                last_ref_frame = ref_frame
            else:
                ref_frame = last_ref_frame

            frame = video.get_frame()
            if frame is None:
                break

            if ref_frame is None:
                audio_player.stop()
                display_frame = frame.copy()
                display_frame = visualizer.draw_end_message(display_frame, text=judge.score)
                video.show(display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    video.release()
                    reference.release()
                    # 🔹 Save user keypoints if enabled
                    if SAVE_KEYPOINTS and len(user_keypoints_seq) > 0:
                        np.savez("assets/keypoints/user_session.npz", keypoints=np.array(user_keypoints_seq))
                        print("User keypoints saved to assets/keypoints/user_session.npz")
                    return
                continue

            # 🔹 Detection
            results = detector.detect(frame)
            if results.pose_landmarks:
                score, stage = judge.update(results.pose_landmarks.landmark, expected_idx=expected_idx, method=METHOD)
                frame = detector.draw(frame, results)
                print(score)
                # 🔹 Collect keypoints if enabled
                if SAVE_KEYPOINTS:
                    user_kp = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark])
                    user_keypoints_seq.append(user_kp)

            ref_frame = visualizer.overlay_pip(ref_frame, frame, size=(300,200))

            video.show(ref_frame)

            # Quit key
            if video.should_quit('q'):
                video.release()
                reference.release()
                # 🔹 Save user keypoints if enabled
                if SAVE_KEYPOINTS and len(user_keypoints_seq) > 0:
                    np.savez("assets/keypoints/user_session_unicorn.npz", keypoints=np.array(user_keypoints_seq))
                    print("User keypoints saved to assets/keypoints/user_session_unicorn.npz")
                return

if __name__ == "__main__":
    main()
