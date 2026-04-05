import pygame

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.tracks = [
            "music/sample_tracks/track1.wav",
            "music/sample_tracks/track2.wav"
        ]
        self.current = 0
        pygame.mixer.music.load(self.tracks[self.current])

    def play(self):
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()

    def next(self):
        self.current = (self.current + 1) % len(self.tracks)
        pygame.mixer.music.load(self.tracks[self.current])
        pygame.mixer.music.play()

    def prev(self):
        self.current = (self.current - 1) % len(self.tracks)
        pygame.mixer.music.load(self.tracks[self.current])
        pygame.mixer.music.play()