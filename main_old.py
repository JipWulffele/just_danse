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

    # 0.  Initialize everything
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

    # 1. Wait for a person
    if not wait_for_person(video, detector, visualizer):
        video.release()
        return

    # 2. Countdown
    countdown(video, 3)

    # 3. Main program: dancing
    start_time = time.time()
    
    while reference.is_open() and video.is_open():
        
        ref_frame = reference.get_frame() # refernce video

        frame = video.get_frame() # webcam stream

        if ref_frame is None or frame is None:
            break

        # Detection and judging on webcam stream
        results = detector.detect(frame)
        if results.pose_landmarks: # Person detected: drawlandmarks, and judge
            score, stage = judge.update(results.pose_landmarks.landmark, method=METHOD)
            frame = detector.draw(frame, results)

        # PiP webcam
        ref_frame = visualizer.overlay_pip(ref_frame, frame, size=(300,200))

        # Show icon
        elapsed = time.time() - start_time
        for icon_cfg in icon_data["icons"]:
            if icon_cfg["start"] <= elapsed <= icon_cfg["end"]:
                ref_frame = visualizer.overlay_icon(ref_frame, icon_cfg["image"],
                                                size=tuple(icon_cfg["size"]))

        video.show(ref_frame)

        if video.should_quit('q'):
            break

    video.release()


if __name__ == "__main__":
    main()