import pygame
import os
from player import MusicPlayer

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 300))
    pygame.display.set_caption("Pro Keyboard Music Player")
    font = pygame.font.SysFont("Segoe UI", 22)
    clock = pygame.time.Clock()

    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_dir = os.path.join(base_dir, "music")
    
    player = MusicPlayer(music_dir)
    
    running = True
    while running:
        
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

        
        screen.fill((25, 25, 25)) # Dark background
        
        track_name, status = player.get_info()
        
        
        title_surf = font.render(f"Track: {track_name}", True, (255, 255, 255))
        status_surf = font.render(f"Status: {status}", True, (0, 255, 150) if player.is_playing else (255, 100, 100))
        hint_surf = font.render("[P] Play/Pause  [S] Stop  [N] Next  [B] Back  [Q] Quit", True, (150, 150, 150))
        
        screen.blit(title_surf, (40, 60))
        screen.blit(status_surf, (40, 110))
        screen.blit(hint_surf, (40, 220))

        
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()

if __name__ == "__main__":
    main()