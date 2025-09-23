import cv2

class Visualizer:
    def draw_count(self, frame, count):
        cv2.putText(frame, f"Score: {count}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        return frame

    def draw_stage(self, frame, stage):
        cv2.putText(frame, f"Stage: {stage}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        return frame
    
    def draw_text(self, frame, text):
        cv2.putText(frame, text, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        return frame
    
    def draw_warning(self, frame, text=None, example_image=None):
        h, w, _ = frame.shape
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (84, 0, 255), -1)
        alpha = 0.5
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        if text:
            cv2.putText(frame, text,
                        (100, 100), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (255, 255, 255), 3, cv2.LINE_AA)

        if example_image is not None:
            # resize and overlay example image bottom right
            ex = cv2.resize(example_image, (200, 200))
            frame[-220:-20, -220:-20] = ex

        return frame
    
    def draw_end_message(self, frame, text=None):
        h, w, _ = frame.shape

        # --- Add semi-transparent colorful overlay ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (84, 0, 255), -1)   # deep blue base
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # --- Add festive border (bright yellow) ---
        cv2.rectangle(frame, (40, 40), (w-40, h-40), (0, 189, 255), 10)

        if text:
            # --- Draw outlined, colorful score text ---
            font = cv2.FONT_HERSHEY_SIMPLEX
            score_text = f"Your Score: {text}"

            # Shadow/outline (black, thicker)
            cv2.putText(frame, score_text, (100, 150), font, 2.5, (255, 255, 255), 8, cv2.LINE_AA)
            # Main text (bright green)
            cv2.putText(frame, score_text, (100, 150), font, 2.5, (153, 0, 57), 5, cv2.LINE_AA)

            # --- Add festive message ---
            message = "Press ENTER to quit | Press D to dance again"
            cv2.putText(frame, message, (100, h - 100), font, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

        return frame
    
    def overlay_pip(self, main_frame, pip_frame, size=(200, 150), margin=20):
        """Overlay webcam stream as picture-in-picture (bottom-left)."""
        pip_resized = cv2.resize(pip_frame, size)
        h, w = pip_resized.shape[:2]
        h_frame, w_frame = main_frame.shape[:2]

        y1 = h_frame - h - margin
        y2 = y1 + h
        x1 = margin
        x2 = x1 + w

        main_frame[y1:y2, x1:x2] = pip_resized
        return main_frame

    def overlay_icon(self, frame, icon, size=(200, 200)):
        """
        Simple, hardcoded icon overlay (bottom-right corner).
        Ignores pos argument and alpha channel.
        """
        # Resize icon
        icon_resized = cv2.resize(icon, size)
        if icon_resized.shape[2] == 4:
            icon_resized = icon_resized[:, :, :3]

        # Overlay at bottom-right
        h_icon, w_icon, _ = icon_resized.shape
        h_frame, w_frame, _ = frame.shape

        # Make sure we don’t go out of bounds
        y1 = h_frame - h_icon - 20  # 20 px margin
        y2 = y1 + h_icon
        x1 = w_frame - w_icon - 20
        x2 = x1 + w_icon

        frame[y1:y2, x1:x2] = icon_resized
        return frame