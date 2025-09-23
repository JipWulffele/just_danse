import cv2

class VideoHandler:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.rotation_angle = 0  # default no rotation
        self.target_width = None
        self.target_height = None

    def is_open(self):
        return self.cap.isOpened()

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Apply rotation if set
        if self.rotation_angle != 0:
            frame = self.rotate_frame(frame, self.rotation_angle)

        # Apply resizing with aspect ratio preservation
        if hasattr(self, 'target_height') and self.target_height is not None:
            frame = self.resize_keep_aspect(frame, self.target_height, getattr(self, 'target_width', None))

        return frame

    def show(self, frame, window_name="Dance App"):
        cv2.imshow(window_name, frame)

    def should_quit(self, key='q'):
        return cv2.waitKey(1) & 0xFF == ord(key)
    
    def set_target_size(self, width=None, height=None):
        """Resize frames keeping aspect ratio and optionally pad width."""
        self.target_width = width
        self.target_height = height
    
    def set_rotation(self, angle):
        """Set rotation angle for all subsequent frames."""
        self.rotation_angle = angle
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    @staticmethod
    def rotate_frame(frame, angle):
        """
        Rotate a frame around its center and expand the canvas so nothing is cropped.
        """
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)

        # Compute rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Compute new bounding dimensions
        cos = abs(M[0, 0])
        sin = abs(M[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)

        # Adjust rotation matrix to take into account translation
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        # Rotate the image
        rotated = cv2.warpAffine(frame, M, (new_w, new_h), borderValue=(0,0,0))
        return rotated
    

    @staticmethod
    def resize_keep_aspect(frame, target_height, target_width=None):
        """
        Resize frame to fit target_height keeping aspect ratio.
        Optionally pad width or height to target_width/target_height.
        Ensures the full frame is visible (no cropping).
        """
        h, w = frame.shape[:2]

        # Compute scale to fit height
        scale = target_height / h
        new_w = int(w * scale)
        resized = cv2.resize(frame, (new_w, target_height))

        # Pad width if needed
        if target_width is not None and new_w < target_width:
            pad_left = (target_width - new_w) // 2
            pad_right = target_width - new_w - pad_left
            resized = cv2.copyMakeBorder(resized, 0, 0, pad_left, pad_right, cv2.BORDER_CONSTANT, value=(0,0,0))
        # Pad height if needed (e.g., for very wide videos)
        h_resized = resized.shape[0]
        w_resized = resized.shape[1]
        if h_resized < target_height:
            pad_top = (target_height - h_resized) // 2
            pad_bottom = target_height - h_resized - pad_top
            resized = cv2.copyMakeBorder(resized, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=(0,0,0))

        return resized