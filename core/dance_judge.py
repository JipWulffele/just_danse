import random

class DanceJudge:
    def __init__(self):
        self.score = 0
        self.stage = None

    def update(self, landmarks, method="distance"):
        """
        landmarks: list of MediaPipe landmarks
        method: "distance based"
        """
        self.score = random.random() # sub. increment score infinitly
        self.stage = "dancing"
        return self.score, self.stage