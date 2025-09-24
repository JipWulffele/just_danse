import pygame
import time

class AudioSyncPlayer:
    def __init__(self, audio_path):
        pygame.mixer.init()
        self.audio_path = audio_path
        self._loaded = False
        self.start_time = None

    def load(self):
        pygame.mixer.music.load(self.audio_path)
        self._loaded = True

    def play(self):
        if not self._loaded:
            self.load()
        pygame.mixer.music.play()
        self.start_time = time.time()

    def stop(self):
        pygame.mixer.music.stop()

    def set_speed(self, speed=1.0):
        # Speed change logic here if needed
        pass

    def get_elapsed(self):
        """Return elapsed time of the audio in seconds."""
        if self.start_time is None:
            return 0
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1:
            return 0
        return pos_ms / 1000.0