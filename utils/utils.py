import time
import cv2

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
            frame = visualizer.draw_text(frame, "Stand in view...")

        video.show(frame)
        if video.should_quit('q'):
            return False
    return False


def countdown(video, seconds=3):
    """Show 3–2–1 countdown."""
    for i in range(seconds, 0, -1):
        frame = video.get_frame()
        if frame is None:
            break

        cv2.putText(frame, str(i), (frame.shape[1]//2 - 50, frame.shape[0]//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 8)
        video.show(frame)
        cv2.waitKey(1000)  # wait 1s