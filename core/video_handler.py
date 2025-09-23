import cv2

class VideoHandler:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)

    def is_open(self):
        return self.cap.isOpened()

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def show(self, frame, window_name="Dance App"):
        cv2.imshow(window_name, frame)

    def should_quit(self, key='q'):
        return cv2.waitKey(1) & 0xFF == ord(key)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
