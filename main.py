import cv2
import time

from utils.utils import wait_for_person, countdown

from core.video_handler import VideoHandler
from core.pose_detector import PoseDetector
from core.dance_judge import DanceJudge
from core.visualizer import Visualizer

# Hyper parameters
SOURCE = 1 # webcam index: check using ```ls /dev/video*```
METHOD = "distance" # Method for calculating the score


def main():

    # 0.  Initialize modules
    video = VideoHandler(source=SOURCE)  # 0 for webcam, or path to video
    detector = PoseDetector()
    judge = DanceJudge()
    visualizer = Visualizer()

    # 1. Wait for a person
    if not wait_for_person(video, detector, visualizer):
        video.release()
        return

    # 2. Countdown
    countdown(video, 3)

    # 3. Main program: dancing
    while video.is_open():
        frame = video.get_frame()
        if frame is None:
            break

        results = detector.detect(frame)

        if results.pose_landmarks:  # Person detected
            score, stage = judge.update(results.pose_landmarks.landmark, method=METHOD)
            frame = detector.draw(frame, results)
            frame = visualizer.draw_count(frame, score)
            frame = visualizer.draw_stage(frame, stage)

        video.show(frame)

        if video.should_quit('q'):
            break

    video.release()


if __name__ == "__main__":
    main()