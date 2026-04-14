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
        
        self.song_length = 0      # Total duration of the file
        self.position_offset = 0  # To track time across pauses/stops if needed
        
        if os.path.exists(music_dir):
            self.playlist = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        
        if not self.playlist:
            print(f"Error: No audio files found in {music_dir}")

    def play_pause(self):
        if not self.playlist:
            return

        if not self.is_playing and not self.is_paused:
            self.load_track()
            pygame.mixer.music.play()
            self.is_playing = True
            
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False

    def load_track(self):
        """Loads the file and calculates its total length."""
        path = os.path.join(self.music_dir, self.playlist[self.current_index])
        pygame.mixer.music.load(path)

        temp_sound = pygame.mixer.Sound(path)
        self.song_length = temp_sound.get_length()

    def stop(self):
        """Stops playback and resets position."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def next_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.reset_and_play()

    def prev_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.reset_and_play()

    def reset_and_play(self):
        """Helper to reset states when changing tracks."""
        self.stop()
        self.play_pause()

    def get_progress(self):
        """Returns current_seconds, total_seconds, and a 0.0-1.0 percentage."""
        if not self.is_playing and not self.is_paused:
            return 0, self.song_length, 0

        current_pos = pygame.mixer.music.get_pos() / 1000.0

        current_pos = min(current_pos, self.song_length)
        
        percent = current_pos / self.song_length if self.song_length > 0 else 0
        return current_pos, self.song_length, percent

    def get_info(self):
        if not self.playlist:
            return "No Music Found", "Error"
        
        status = "Playing" if self.is_playing else ("Paused" if self.is_paused else "Stopped")
        return self.playlist[self.current_index], status