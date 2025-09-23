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