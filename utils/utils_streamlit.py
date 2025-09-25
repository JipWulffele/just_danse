import time
import cv2
import json
import os
import pygame

IMG_START_POSITION = cv2.imread("assets/images/icon_start.png")

def load_icons(config_path):
    """
    Loads icons from JSON config and returns a list of icon info with images.
    """
    with open(config_path, "r") as f:
        data = json.load(f)

    # Base path for images
    base_path = os.path.join(os.path.dirname(config_path), "../images")

    for icon_cfg in data["icons"]:
        icon_file = os.path.join(base_path, os.path.basename(icon_cfg["file"]))
        icon_cfg["image"] = cv2.imread(icon_file, cv2.IMREAD_UNCHANGED)
        if icon_cfg["image"] is None:
            print(f"[WARNING] Failed to load icon: {icon_file}")
    return data


def wait_for_person(video, detector, visualizer):
    """Keep showing webcam until a person with nose, hip, and feet is detected."""
    print("Waiting for person...")

    while video.is_open():
        frame = video.get_frame()
        if frame is None:
            break

        results = detector.detect(frame)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            required = [0, 23, 24, 27, 28, 31, 32]  # nose, hips, ankles, feet
            if all(lm[i].visibility > 0.6 for i in required):
                print("Person detected!")
                return True, frame

            frame = detector.draw(frame, results)

        frame = visualizer.draw_warning(frame, "Please position correctly", IMG_START_POSITION)

        # Instead of video.show(), just return frame to Streamlit
        return False, frame

    return False, None


def countdown(video, seconds=3, frame_window=None):
    """Run live video in Streamlit while showing a countdown overlay."""

    # Init audio
    pygame.mixer.init(buffer=256)
    beep = pygame.mixer.Sound("assets/audio/beep-01a.wav")

    # Warm up mixer
    beep.set_volume(0.0)
    beep.play()
    pygame.time.delay(50)
    beep.stop()
    beep.set_volume(1.0)
    pygame.time.delay(100)

    start = time.time()
    end = start + seconds
    last_remaining = seconds + 1

    while time.time() < end:
        frame = video.get_frame()
        if frame is None:
            break

        remaining = int(end - time.time()) + 1

        if remaining != last_remaining:
            beep.play(maxtime=200)
            last_remaining = remaining

        # Draw countdown text
        cv2.putText(frame, str(remaining),
                    (frame.shape[1]//2 - 50, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 8,
                    (255, 255, 255), 32, lineType=cv2.LINE_AA)
        cv2.putText(frame, str(remaining),
                    (frame.shape[1]//2 - 50, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 8,
                    (84, 0, 255), 24, lineType=cv2.LINE_AA)

        # Show frame in Streamlit
        if frame_window is not None:
            frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        time.sleep(0.02)  # small delay to avoid overload

    return frame