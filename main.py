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
SOURCE = 0 # webcam index: check using ```ls /dev/video*```
METHOD = "distance" # Method for calculating the score
REF_VIDEO = "assets/video/reference.webm" # path to reference video
REF_KEYPOINTS="assets/keypoints/keypoints_reference1.npz" # path to reference keypoints
ICON_PATH = "assets/config/icon_schedule.json"
AUDIO_PATH = "assets/audio/de_kabouter_dans_ultra_short_2.mp3"
FRAME_WIDTH = 1080
FRAME_HEIGHT = 720
WEBCAM_ROTATION = 90
FORCE_FPS = 0 # force frame rate during reference video -> 0 = play at normal speed (25 fps)


def main():

    ecran = Ecran() # Start screen

    video = VideoHandler(source=SOURCE)  # 0 for webcam, or path to video
    video.set_rotation(WEBCAM_ROTATION)
    video.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    reference = VideoHandler(source=REF_VIDEO)
    reference.set_rotation(90)
    reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    audio_player = AudioSyncPlayer(AUDIO_PATH)

    detector = PoseDetector()

    data = np.load(REF_KEYPOINTS)
    ref_keypoints_seq = data["keypoints"]
    judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20], angle_deg=WEBCAM_ROTATION)
    
    visualizer = Visualizer()
    
    icon_data = load_icons(ICON_PATH)

    # Show a sticker every 2 s
    last_sticker_time = 0    # timestamp of last sticker shown
    sticker_start_time = 0
    sticker_interval = 3.0   # every x seconds
    sticker_duration = 1.5   # show sticker for x seconds
    current_sticker_score = 1

    # Show starting screen for 2 seconds
    start_screen_frame = ecran.get_ecran_start(size=(FRAME_WIDTH , FRAME_HEIGHT))
    ecran.show_ecran(video, reference, start_screen_frame, 2)

    while True:  # Main loop: allows relaunching

        # 1. Wait for person
        if not wait_for_person(video, detector, visualizer):
            video.release()
            return

        # 2. Countdown
        countdown(video, 3)

        # 3. Set up frame counting
        if FORCE_FPS == 0: # play at normal speed
            ref_fps = reference.cap.get(cv2.CAP_PROP_FPS)
        else: # play at speed set by FORCE_FPS
            ref_fps = FORCE_FPS
        frame_duration = 1.0 / ref_fps
        ref_frame_idx = 0
        last_ref_frame = None
        
        # 4. Dance session
        audio_player.play()
        start_time = time.time()

        while video.is_open():

            loop_start = time.time() # keep track of time
            elapsed = time.time() - start_time # total elapsed time

            expected_idx = int(elapsed / frame_duration)
            
            if expected_idx > ref_frame_idx:
                # Advance as many frames as needed
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

            # Reference video ended
            if ref_frame is None:
                if ref_frame_idx == 0: # At the begining the index might be 0 for some frames
                    display_frame = frame.copy() # Get frame from webcam as fallback
                    video.show(display_frame)
                    continue

                else: # only stop when reference video finished playing
                    audio_player.stop()
                    
                    # Draw a placeholder square
                    display_frame = frame.copy() # Get frame from webcam as fallback
                    display_frame = visualizer.draw_end_message(display_frame, text=judge.score)
                    video.show(display_frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        video.release()
                        reference.release()
                        return
                    elif key == ord('d'):
                        # Restart reference video
                        reference.release()
                        reference = VideoHandler(source=REF_VIDEO)
                        reference.set_rotation(90)
                        reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)
                        # Restart sticker
                        last_sticker_time = 0   
                        sticker_start_time = 0
                        # Restart count
                        judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20])
                        ref_frame_idx = 0
                        start_time = time.time()
                        break
                    continue

            # Detection and judging
            results = detector.detect(frame)
            if results.pose_landmarks:
                score, stage = judge.update(results.pose_landmarks.landmark, expected_idx=expected_idx, method=METHOD) # prend expected_idx
                frame = detector.draw(frame, results)

            # PiP webcam
            ref_frame = visualizer.overlay_pip(ref_frame, frame, size=(300,200))

            # Overlay icons
            for icon_cfg in icon_data["icons"]:
                if icon_cfg["start_frame"] <= ref_frame_idx <= icon_cfg["end_frame"]:
                    ref_frame = visualizer.overlay_icon(
                        ref_frame, icon_cfg["image"], size=tuple(icon_cfg["size"])
                    )

            # Check if it's time to show a new sticker
            if elapsed - last_sticker_time >= sticker_interval:
                show_sticker = True
                last_sticker_time = elapsed  # reset last shown time
                sticker_start_time = elapsed # when we started showing this sticker
                current_sticker_score = judge.score
                print(f"Raw score (for debugging): {judge.score}")
            else:
                show_sticker = False

            # Keep showing sticker for sticker_duration
            if current_sticker_score and (show_sticker or (elapsed - sticker_start_time <= sticker_duration)):
                ref_frame = visualizer.overlay_score_sticker(ref_frame, current_sticker_score)

            video.show(ref_frame)

            # Slow down to match FPS
            loop_time = time.time() - loop_start
            delay = max(0, frame_duration - loop_time)
            time.sleep(delay)

            # Quit
            if video.should_quit('q'):
                video.release()
                reference.release()
                return

if __name__ == "__main__":
    main()