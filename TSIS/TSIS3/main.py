import pygame, sys, os
from ui import Button
from persistence import load_data, save_data, update_leaderboard
from racer import play_game, game_over_screen

pygame.init()
SCREEN = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Gemini Racer")
FONT = pygame.font.SysFont("Verdana", 20)
IMG_DIR = r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS3\assets"

def main_menu():
    username = "Player1"; active_input = False
    while True:
        # Constant Refresh of Settings
        sets = load_data("settings.json", {"color": "red", "difficulty": 1, "music": True})
        
        # Kill music if turned off elsewhere
        if not sets.get('music', True) and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        SCREEN.fill((200, 200, 200))
        input_rect = pygame.Rect(100, 80, 200, 35)
        pygame.draw.rect(SCREEN, (255,255,255) if active_input else (230,230,230), input_rect)
        SCREEN.blit(FONT.render(username, True, (0,0,0)), (input_rect.x + 5, input_rect.y + 5))
        
        b_play = Button("PLAY", 100, 150, 200, 50, (100, 255, 100), (150, 255, 150))
        b_set  = Button("SETTINGS", 100, 230, 200, 50, (100, 100, 255), (150, 150, 255))
        b_lb   = Button("LEADERBOARD", 100, 310, 200, 50, (255, 255, 100), (255, 255, 150))
        b_quit = Button("QUIT", 100, 390, 200, 50, (255, 100, 100), (255, 150, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: active_input = input_rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE: username = username[:-1]
                else: username += event.unicode
            if b_play.is_clicked(event):
                playing = True
                while playing:
                    res = play_game(SCREEN, sets)
                    if res:
                        update_leaderboard(username, res['score'], res['distance'])
                        if game_over_screen(SCREEN, res) == "menu": playing = False
                    else: playing = False
            if b_set.is_clicked(event): settings_screen()
            if b_lb.is_clicked(event): leaderboard_screen()
            if b_quit.is_clicked(event): pygame.quit(); sys.exit()
            
        for b in [b_play, b_set, b_lb, b_quit]: b.draw(SCREEN)
        pygame.display.update()

def settings_screen():
    sets = load_data("settings.json", {"color": "red", "difficulty": 1, "music": True})
    colors = ["red", "white", "blue"]
    while True:
        SCREEN.fill((220, 220, 220))
        m_txt = "ON" if sets.get('music', True) else "OFF"
        b_music = Button(f"Music: {m_txt}", 100, 70, 200, 50, (255,255,255), (200,200,200))
        b_color = Button(f"Car: {sets['color'].upper()}", 100, 150, 200, 50, (255,255,255), (200,200,200))
        b_diff  = Button(f"Diff: {sets['difficulty']}", 100, 230, 200, 50, (255,255,255), (200,200,200))
        b_back  = Button("SAVE & BACK", 100, 400, 200, 50, (150,150,150), (180,180,180))
        
        for event in pygame.event.get():
            if b_back.is_clicked(event): save_data("settings.json", sets); return
            if b_music.is_clicked(event):
                sets['music'] = not sets.get('music', True)
                if not sets['music']: pygame.mixer.music.stop()
                else: 
                    try: 
                        pygame.mixer.music.load(os.path.join(IMG_DIR, "music_2.mp3"))
                        pygame.mixer.music.play(-1)
                    except: pass
            if b_diff.is_clicked(event): sets['difficulty'] = (sets['difficulty'] % 3) + 1
            if b_color.is_clicked(event): sets['color'] = colors[(colors.index(sets['color']) + 1) % len(colors)]
        
        for b in [b_music, b_color, b_diff, b_back]: b.draw(SCREEN)
        pygame.display.update()

def leaderboard_screen():
    scores = load_data("leaderboard.json", [])
    while True:
        SCREEN.fill((30, 30, 30))
        b_back = Button("BACK", 150, 520, 100, 40, (150,150,150), (200,200,200))
        for i, entry in enumerate(scores[:10]):
            txt = FONT.render(f"{i+1}. {entry['name']} - {entry['score']}", True, (255,255,255))
            SCREEN.blit(txt, (50, 80 + i * 35))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if b_back.is_clicked(event): return
        b_back.draw(SCREEN); pygame.display.update()

if __name__ == "__main__": main_menu()