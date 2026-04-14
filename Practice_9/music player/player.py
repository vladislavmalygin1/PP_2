import pygame
import os

class MusicPlayer:
    def __init__(self, music_dir):
        pygame.mixer.init()
        self.music_dir = music_dir
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False

        if os.path.exists(music_dir):
            self.playlist = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        
        if not self.playlist:
            print(f"Warning: No music files found in {music_dir}")

    def play_pause(self):
        if not self.playlist:
            return

        if not self.is_playing and not self.is_paused:
            path = os.path.join(self.music_dir, self.playlist[self.current_index])
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                self.is_playing = True
            except pygame.error as e:
                print(f"Error loading {path}: {e}")
        
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def next_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.is_paused = False 
        self.is_playing = False
        self.play_pause()

    def prev_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.is_paused = False
        self.is_playing = False
        self.play_pause()

    def get_info(self):
        if not self.playlist:
            return "No Music Found", "Stopped"
        status = "Playing" if self.is_playing else ("Paused" if self.is_paused else "Stopped")
        return self.playlist[self.current_index], status