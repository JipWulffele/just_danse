import cv2
import numpy as np

class Visualizer:
    def __init__(self, difficulty_levels='Medium'):
        self.difficulty_levels = difficulty_levels
        self.difficulty_penalty = {
            'Easy': -0.1,
            'Medium': 0.0,
            'Hard': 0.1
        }.get(self.difficulty_levels, 0.0)

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

        if text:
            score_str = self.score_to_text(text)

        # color based on score
        if score_str == "Excellent":
            bg_color = (153, 0, 57)
        elif score_str == "Bon":
            bg_color = (89, 0, 158)
        elif score_str == "Moyen":
            bg_color = (84, 0, 255)
        elif score_str == "Faible":
            bg_color = (0, 84, 255)
        else:
            bg_color = (0, 189, 255)

        # --- Semi-transparent overlay ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0, 0, 255), -1)
        alpha = 0
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # --- Festive border ---
        cv2.rectangle(frame, (40, 40), (w-40, h-40), bg_color, 10)

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 4
        max_width = w - 200

        if text:
            # --- First line: "Final Score:" ---
            label = "Final Score:"
            label_scale = 2.0
            (label_w, label_h), _ = cv2.getTextSize(label, font, label_scale, thickness)
            while label_w > max_width and label_scale > 0.5:
                label_scale -= 0.1
                (label_w, label_h), _ = cv2.getTextSize(label, font, label_scale, thickness)

            x_label = (w - label_w) // 2
            y_label = (h // 2) - 50  # center a bit upward

            cv2.putText(frame, label, (x_label, y_label), font, label_scale,
                        (0, 0, 0), thickness, cv2.LINE_AA)

            # --- Second line: the score itself ---
            score_scale = 3.0
            (score_w, score_h), _ = cv2.getTextSize(score_str, font, score_scale, thickness)
            while score_w > max_width and score_scale > 0.5:
                score_scale -= 0.1
                (score_w, score_h), _ = cv2.getTextSize(score_str, font, score_scale, thickness)

            x_score = (w - score_w) // 2
            y_score = y_label + score_h + 40  # below the label with spacing

            cv2.putText(frame, score_str, (x_score, y_score), font, score_scale,
                        bg_color, thickness+2, cv2.LINE_AA)

        if restart_message:
            message = "Press 'q' to quit | Press 'd' to dance again"
            msg_font_scale = 1.2
            (msg_w, msg_h), _ = cv2.getTextSize(message, font, msg_font_scale, 3)
            while msg_w > w - 200 and msg_font_scale > 0.5:
                msg_font_scale -= 0.1
                (msg_w, msg_h), _ = cv2.getTextSize(message, font, msg_font_scale, 3)

            # Centered at bottom
            x_msg = (w - msg_w) // 2
            y_msg = h - 80
            cv2.putText(frame, message, (x_msg, y_msg), font, msg_font_scale,
                        (0, 0, 0), 3, cv2.LINE_AA)

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

        # color based on score
        if text == "Excellent":
            bg_color = (153, 0, 57)
        elif text == "Bon":
            bg_color = (89, 0, 158)
        elif text == "Moyen":
            bg_color = (84, 0, 255)
        elif text == "Faible":
            bg_color = (0, 84, 255)
        else:
            bg_color = (0, 189, 255)

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
        if norm < 0.3 + self.difficulty_penalty:
            return "Trop nul"
        elif norm < 0.6 + self.difficulty_penalty:
            return "Faible"
        elif norm < 0.75 + self.difficulty_penalty:
            return "Moyen"
        elif norm < 0.9 + self.difficulty_penalty:
            return "Bon"
        else:
            return "Excellent"

