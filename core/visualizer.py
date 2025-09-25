import cv2
import numpy as np

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
    
    def draw_end_message(self, frame, text=None, restart_message=True):
        h, w, _ = frame.shape

        # --- Semi-transparent overlay ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (84, 0, 255), -1)
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # --- Festive border ---
        cv2.rectangle(frame, (40, 40), (w-40, h-40), (0, 189, 255), 10)

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 4
        max_width = w - 200  # max width inside rectangle
        font_scale = 2.5     # initial guess

        if text:
            text = self.score_to_text(text)
            score_text = f"Your Score: {text}"
            
            # Reduce font_scale until text fits
            (text_w, text_h), baseline = cv2.getTextSize(score_text, font, font_scale, thickness)
            while text_w > max_width and font_scale > 0.5:
                font_scale -= 0.1
                (text_w, text_h), baseline = cv2.getTextSize(score_text, font, font_scale, thickness)

            # Draw shadow/outline
            cv2.putText(frame, score_text, (100, 150), font, font_scale, (255, 255, 255), thickness+2, cv2.LINE_AA)
            # Draw main text
            cv2.putText(frame, score_text, (100, 150), font, font_scale, (153, 0, 57), thickness, cv2.LINE_AA)

        # Festive message below
        if restart_message:
            message = "Press 'q' to quit | Press 'd' to dance again"
            msg_font_scale = 1.2
            (msg_w, msg_h), _ = cv2.getTextSize(message, font, msg_font_scale, 3)
            # Optionally shrink message if too wide
            while msg_w > w - 200 and msg_font_scale > 0.5:
                msg_font_scale -= 0.1
                (msg_w, msg_h), _ = cv2.getTextSize(message, font, msg_font_scale, 3)
            cv2.putText(frame, message, (100, h - 100), font, msg_font_scale, (255, 255, 255), 3, cv2.LINE_AA)

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
    

    def overlay_score_sticker(self, frame, score):
        """
        Overlay a score sticker on the frame (top-right corner, rotated, solid background).
        Handles rotation without cropping and places it nicely inside the frame.
        """

        # Convert score to text
        text = self.score_to_text(score)

        # Parameters
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        text_padding = 20   # bigger padding around text
        box_padding = 40    # extra space around the box
        margin = 40
        bg_color = (153, 0, 57)
        text_color = (255, 255, 255)

        # Measure text size
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # Sticker dimensions (bigger than text)
        sticker_w = text_w + 2*text_padding + box_padding
        sticker_h = text_h + 2*text_padding + box_padding

        # Create sticker
        sticker = np.zeros((sticker_h, sticker_w, 3), dtype=np.uint8)
        sticker[:] = bg_color

        # Draw text centered
        text_x = (sticker_w - text_w) // 2
        text_y = (sticker_h + text_h) // 2
        cv2.putText(sticker, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

        # Overlay on frame (top-right)
        h_frame, w_frame, _ = frame.shape
        y1 = margin
        x1 = w_frame - sticker_w - margin
        y2 = y1 + sticker_h
        x2 = x1 + sticker_w

        frame[y1:y2, x1:x2] = sticker
        return frame


    def score_to_text(self, score, min_score=0.31, max_score=0.7):
        """
        Map a numeric score to a textual rating.
        Lower scores are better: 0.3 → Excellent, 0.7 → Trop nul.
        """
        # Clip to range
        score_clipped = np.clip(score, min_score, max_score)

        # Invert normalization so lower is better
        norm = (max_score - score_clipped) / (max_score - min_score)

        # Map to text
        if norm < 0.3:
            return "Trop nul"
        elif norm < 0.6:
            return "Faible"
        elif norm < 0.75:
            return "Moyen"
        elif norm < 0.9:
            return "Bon"
        else:
            return "Excellent"

