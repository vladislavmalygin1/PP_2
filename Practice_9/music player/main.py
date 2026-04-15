import pygame
import os
from player import MusicPlayer

WIDTH, HEIGHT = 600, 320
BG_COLOR = (20, 20, 20)
ACCENT_COLOR = (0, 255, 150)  
TEXT_COLOR = (230, 230, 230)
BAR_BG = (60, 60, 60)

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def main():

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Keyboard Music Player")
    
    font_main = pygame.font.SysFont("Segoe UI", 24, bold=True)
    font_sub = pygame.font.SysFont("Segoe UI", 18)
    clock = pygame.time.Clock()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_dir = os.path.join(base_dir, "music")
    
    player = MusicPlayer(music_dir)
    
    running = True
    while running:
        # 3. Event Handling (The "Controller")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play_pause()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    running = False

        screen.fill(BG_COLOR)
        
        track_name, status, cur_index = player.get_info()
        current_s, total_s, percent = player.get_progress()

        track_surf = font_main.render(f"Track {cur_index + 1}: {track_name}", True, TEXT_COLOR)
        status_surf = font_sub.render(f"Status: {status}", True, ACCENT_COLOR if player.is_playing else (180, 0, 0))
        
        bar_x, bar_y = 50, 180
        bar_w, bar_h = 500, 8
        # Background of the bar
        pygame.draw.rect(screen, BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        if total_s > 0:
            pygame.draw.rect(screen, ACCENT_COLOR, (bar_x, bar_y, int(bar_w * percent), bar_h), border_radius=4)

        time_str = f"{format_time(current_s)} / {format_time(total_s)}"
        time_surf = font_sub.render(time_str, True, (150, 150, 150))
        
        controls_hint = font_sub.render("[P] Play/Pause  [S] Stop  [N] Next  [B] Back  [Q] Quit", True, (100, 100, 100))

        screen.blit(track_surf, (50, 60))
        screen.blit(status_surf, (50, 100))
        screen.blit(time_surf, (50, 200))
        screen.blit(controls_hint, (50, 260))

        
        pygame.display.flip()
        clock.tick(60)  

    pygame.quit()

if __name__ == "__main__":
    main()