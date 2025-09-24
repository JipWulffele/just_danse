import json
import time
import cv2
import numpy as np

from utils.utils import wait_for_person, countdown, load_icons

from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.dance_judge import DanceJudge
from core.visualizer import Visualizer

# Hyper parameters
SOURCE = 0 # webcam index: check using ```ls /dev/video*```
METHOD = "distance" # Method for calculating the score
REF_VIDEO = "assets/video/reference.webm" # path to reference video
REF_KEYPOINTS="assets/keypoints/keypoints_reference1.npz" # path to reference keypoints
ICON_PATH = "assets/config/icon_schedule.json"
FRAME_WIDTH = 1080
FRAME_HEIGHT = 720
WEBCAM_ROTATION = 90


def main():

    video = VideoHandler(source=SOURCE)  # 0 for webcam, or path to video
    video.set_rotation(WEBCAM_ROTATION)
    video.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    reference = VideoHandler(source=REF_VIDEO)
    reference.set_rotation(90)
    reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    detector = PoseDetector()
    data = np.load(REF_KEYPOINTS)
    ref_keypoints_seq = data["keypoints"]
    judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20])
    visualizer = Visualizer()
    
    icon_data = load_icons(ICON_PATH)

    # 🔹 Storage for user keypoints
    user_keypoints_seq = []

    # Show a sticker every 2 s
    last_sticker_time = 0   # timestamp of last sticker shown
    sticker_start_time = 0
    sticker_interval = 3.0    # every x seconds
    sticker_duration = 1.5    # show sticker for x seconds
    current_sticker_score = 1
    while True:  # allows relaunching

        if not wait_for_person(video, detector, visualizer):
            video.release()
            return

        countdown(video, 3)
        start_time = time.time()

        while video.is_open():
            ref_frame = reference.get_frame()
            frame = video.get_frame()

            if frame is None:
                break

            if ref_frame is None:
                display_frame = frame.copy()
                display_frame = visualizer.draw_end_message(display_frame, text=judge.score)
                video.show(display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    video.release()
                    reference.release()
                    # 🔹 Save collected keypoints
                    if len(user_keypoints_seq) > 0:
                        np.savez("assets/keypoints/user_session.npz", keypoints=np.array(user_keypoints_seq))
                        print("User keypoints saved to assets/keypoints/user_session.npz")
                    return
                elif key == ord('d'):
                    reference.release()
                    reference = VideoHandler(source=REF_VIDEO)
                    reference.set_rotation(90)
                    reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

                    # Restart sticker
                    last_sticker_time = 0   
                    sticker_start_time = 0                    
                    judge = DanceJudge(ref_keypoints_seq, shifts=[0,5,10,14,16,18,20])

                    start_time = time.time()
                    break
                continue

            results = detector.detect(frame)
            if results.pose_landmarks:
                score, stage = judge.update(results.pose_landmarks.landmark, WEBCAM_ROTATION, method=METHOD)
                frame = detector.draw(frame, results)

                # 🔹 Collect keypoints
                user_kp = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark])
                user_keypoints_seq.append(user_kp)

            ref_frame = visualizer.overlay_pip(ref_frame, frame, size=(300,200))

            elapsed = time.time() - start_time
            for icon_cfg in icon_data["icons"]:
                if icon_cfg["start"] <= elapsed <= icon_cfg["end"]:
                    ref_frame = visualizer.overlay_icon(ref_frame, icon_cfg["image"],
                                                       size=tuple(icon_cfg["size"]))
# Check if it's time to show a new sticker
            if elapsed - last_sticker_time >= sticker_interval:
                show_sticker = True
                last_sticker_time = elapsed  # reset last shown time
                sticker_start_time = elapsed # when we started showing this sticker
                current_sticker_score = judge.score
                print(judge.score)
            else:
                show_sticker = False

            # Keep showing sticker for sticker_duration
            if current_sticker_score and (show_sticker or (elapsed - sticker_start_time <= sticker_duration)):
                ref_frame = visualizer.overlay_score_sticker(ref_frame, current_sticker_score)

         
            video.show(ref_frame)

            if video.should_quit('q'):
                video.release()
                reference.release()
                # 🔹 Save collected keypoints
                if len(user_keypoints_seq) > 0:
                    np.savez("assets/keypoints/user_session.npz", keypoints=np.array(user_keypoints_seq))
                    print("User keypoints saved to assets/keypoints/user_session.npz")
                return

if __name__ == "__main__":
    main()