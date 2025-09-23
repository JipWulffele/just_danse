import time
import cv2
import json
import os

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
            # Extract needed landmarks
            lm = results.pose_landmarks.landmark
            required = [0, 23, 24, 27, 28, 31, 32]  # nose, hips, ankles, feet
            if all(lm[i].visibility > 0.6 for i in required):
                print("Person detected!")
                return True

            frame = detector.draw(frame, results)
        
        frame = visualizer.draw_warning(frame, "Please position correctly", IMG_START_POSITION)
            
        video.show(frame)
        if video.should_quit('q'):
            return False
    return False


def countdown(video, seconds=3):
    """Run live video while showing a countdown overlay."""
    start = time.time()
    end = start + seconds

    while time.time() < end:
        frame = video.get_frame()
        if frame is None:
            break

        # Remaining whole seconds
        remaining = int(end - time.time()) + 1  
        
        # Outline
        cv2.putText(frame, str(remaining),
                    (frame.shape[1]//2 - 50, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 8,
                  (255, 255, 255), 32, lineType=cv2.LINE_AA)
        # Main text
        cv2.putText(frame, str(remaining),
                    (frame.shape[1]//2 - 50, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 8,
                    (84, 0, 255), 24, lineType=cv2.LINE_AA)

        video.show(frame)

        # Run at normal video speed
        if video.should_quit('q'):
            break