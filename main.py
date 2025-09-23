import json
import time
import cv2

from utils.utils import wait_for_person, countdown, load_icons

from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.dance_judge import DanceJudge
from core.visualizer import Visualizer

# Hyper parameters
SOURCE = 1 # webcam index: check using ```ls /dev/video*```
METHOD = "distance" # Method for calculating the score
REF_VIDEO = "assets/video/reference.webm" # path to reference video
ICON_PATH = "assets/config/icon_schedule.json"
FRAME_WIDTH = 1080
FRAME_HEIGHT = 720
WEBCAM_ROTATION = -90


def main():

    video = VideoHandler(source=SOURCE)  # 0 for webcam, or path to video
    video.set_rotation(WEBCAM_ROTATION)
    video.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    reference = VideoHandler(source=REF_VIDEO)
    reference.set_rotation(90)
    reference.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    detector = PoseDetector()
    judge = DanceJudge()
    visualizer = Visualizer()
    
    icon_data = load_icons(ICON_PATH)

    while True:  # allows relaunching

        # 1. Wait for person
        if not wait_for_person(video, detector, visualizer):
            video.release()
            return

        # 2. Countdown
        countdown(video, 3)

        # 3. Dance session
        start_time = time.time()

        while video.is_open():
            ref_frame = reference.get_frame()  # reference video
            frame = video.get_frame()          # webcam stream

            if frame is None:
                break  # webcam disconnected

            # Reference video ended
            if ref_frame is None:
                display_frame = frame.copy()

                # Draw a placeholder square
                display_frame = visualizer.draw_end_message(display_frame, text=f"{judge.score}")
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
                    start_time = time.time()
                    break
                continue

            # Detection and judging
            results = detector.detect(frame)
            if results.pose_landmarks:
                score, stage = judge.update(results.pose_landmarks.landmark, method=METHOD)
                frame = detector.draw(frame, results)

            # PiP webcam
            ref_frame = visualizer.overlay_pip(ref_frame, frame, size=(300,200))

            # Overlay icons
            elapsed = time.time() - start_time
            for icon_cfg in icon_data["icons"]:
                if icon_cfg["start"] <= elapsed <= icon_cfg["end"]:
                    ref_frame = visualizer.overlay_icon(ref_frame, icon_cfg["image"],
                                                       size=tuple(icon_cfg["size"]))

            video.show(ref_frame)

            # Quit
            if video.should_quit('q'):
                video.release()
                reference.release()
                return


if __name__ == "__main__":
    main()