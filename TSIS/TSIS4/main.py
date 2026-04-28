import pygame
import sys
import os
import db
import config
from game import SnakeGame, WIDTH, HEIGHT, BLOCK_SIZE

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize sound engine

conf = config.load_settings()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
f_s = pygame.font.SysFont("bahnschrift", 20)
f_l = pygame.font.SysFont("bahnschrift", 40)

class Controller:
    def __init__(self):
        self.state = "MENU"
        self.user = ""
        self.uid = None
        self.pb = 0
        self.game = SnakeGame(conf["snake_color"])
        db.init_db()
        self.manage_music()

    def manage_music(self):
        if conf["sound"]:
        # Get the directory where main.py is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the path relative to main.py
            path = os.path.join(base_dir, "assets", "music_1.mp3") 
        
            if os.path.exists(path):
                try:
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play(-1)
                except pygame.error as e:
                    print(f"Pygame couldn't play the file: {e}")
            else:
            # This will print the EXACT path the computer is looking at
                print(f"DEBUG: Looking for music at: {path}") 
        else:
            pygame.mixer.music.stop()

    def btn(self, txt, x, y, w, h, c, hc):
        m, clk = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, hc if r.collidepoint(m) else c, r, border_radius=5)
        t = f_s.render(txt, True, (255, 255, 255))
        screen.blit(t, (x + (w - t.get_width()) // 2, y + (h - t.get_height()) // 2))
        if r.collidepoint(m) and clk[0]:
            pygame.time.delay(150)
            return True
        return False

    def menu_screen(self):
        screen.fill((20, 20, 25))
        title = f_l.render("SNAKE ADVENTURE", True, (0, 255, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        u_t = f_s.render(f"User: {self.user}_", True, (255, 255, 255))
        screen.blit(u_t, (WIDTH // 2 - u_t.get_width() // 2, 110))
        
        if self.btn("PLAY", 225, 170, 150, 40, (0, 100, 0), (0, 150, 0)) and self.user:
            self.uid = db.get_or_create_user(self.user)
            self.pb = db.get_personal_best(self.uid)[0]
            self.state = "GAME"

        if self.btn("LEADERBOARD", 225, 220, 150, 40, (0, 50, 100), (0, 80, 150)): self.state = "LEADER"
        if self.btn("SETTINGS", 225, 270, 150, 40, (60, 60, 60), (90, 90, 90)): self.state = "SET"
        if self.btn("QUIT", 225, 320, 150, 40, (100, 0, 0), (150, 0, 0)): pygame.quit(); sys.exit()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE: self.user = self.user[:-1]
                elif len(self.user) < 10: self.user += e.unicode
        pygame.display.update()

    def settings_screen(self):
        screen.fill((40, 40, 45))
        t = f_l.render("SETTINGS", True, (255, 255, 255))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 40))

        if self.btn(f"Sound: {'ON' if conf['sound'] else 'OFF'}", 200, 100, 200, 40, (60,60,60), (90,90,90)):
            conf['sound'] = not conf['sound']
            self.manage_music()

        if self.btn(f"Grid: {'ON' if conf['grid_overlay'] else 'OFF'}", 200, 150, 200, 40, (60,60,60), (90,90,90)):
            conf['grid_overlay'] = not conf['grid_overlay']

        # Color Cycle
        colors = {"Green": (0,255,0), "Cyan": (0,255,255), "Gold": (255,215,0)}
        for i, (name, col) in enumerate(colors.items()):
            bg = col if tuple(conf['snake_color']) == col else (30,30,30)
            if self.btn(name, 120 + (i*125), 210, 110, 40, bg, col):
                conf['snake_color'] = list(col)
                self.game.snake_color = col

        if self.btn("SAVE & BACK", 225, 300, 150, 40, (0, 100, 0), (0, 150, 0)):
            config.save_settings(conf)
            self.state = "MENU"

        pygame.display.update()
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    def leader_screen(self):
        screen.fill((10, 10, 15))
        data = db.get_leaderboard()
        for i, r in enumerate(data):
            # i+1: rank, r[0]: name, r[1]: score, r[2]: level, r[3]: date
            txt = f_s.render(f"{i+1}. {r[0]} | {r[1]} pts | Lvl {r[2]} | {r[3]}", True, (255, 255, 255))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 60 + i*28))
        
        if self.btn("BACK", 250, 350, 100, 35, (100, 100, 100), (150, 150, 150)): self.state = "MENU"
        pygame.display.update()
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    def play_game(self):
        now = pygame.time.get_ticks()
        
        # 1. Event Handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and self.game.dx == 0: self.game.dx, self.game.dy = -BLOCK_SIZE, 0
                elif e.key == pygame.K_RIGHT and self.game.dx == 0: self.game.dx, self.game.dy = BLOCK_SIZE, 0
                elif e.key == pygame.K_UP and self.game.dy == 0: self.game.dy, self.game.dx = -BLOCK_SIZE, 0
                elif e.key == pygame.K_DOWN and self.game.dy == 0: self.game.dy, self.game.dx = BLOCK_SIZE, 0

        # 2. Logic Update
        if self.game.update() == "DEAD":
            db.save_game(self.uid, self.game.score, self.game.level)
            self.pb = db.get_personal_best(self.uid)[0]
            self.state = "OVER"
            return

        # 3. Drawing
        screen.fill((10, 10, 15)) # Darker background for contrast
        
        if conf['grid_overlay']:
            for x in range(0, WIDTH, BLOCK_SIZE): pygame.draw.line(screen, (30,30,30), (x,0), (x,HEIGHT))
            for y in range(0, HEIGHT, BLOCK_SIZE): pygame.draw.line(screen, (30,30,30), (0,y), (WIDTH,y))
        # --- DRAW POISONED FOOD ---
        # If this doesn't show up, ensure self.game.poison is initialized in reset()
        pygame.draw.rect(screen, (150, 0, 200), [self.game.poison[0], self.game.poison[1], BLOCK_SIZE, BLOCK_SIZE])

        # Draw Power-up (Blue Circle)
        if self.game.powerup:
            pygame.draw.circle(screen, (0, 150, 255), (self.game.powerup['pos'][0]+10, self.game.powerup['pos'][1]+10), 8)

        # Draw Snake & Normal Food
        for s in self.game.snake: 
            pygame.draw.rect(screen, conf['snake_color'], [s[0], s[1], BLOCK_SIZE, BLOCK_SIZE])
        
        pygame.draw.rect(screen, self.game.food['color'], [self.game.food['pos'][0], self.game.food['pos'][1], BLOCK_SIZE, BLOCK_SIZE])

        # Draw Obstacles (Barriers)
        for o in self.game.obstacles: 
            pygame.draw.rect(screen, (100, 100, 100), [o[0], o[1], BLOCK_SIZE, BLOCK_SIZE])
        
        # --- HUD (The Text) ---
        # Added 'Level' to the text string here:
        hud_text = f"Score: {self.game.score} | Level: {self.game.level} | PB: {self.pb}"
        
        # Visual indicators for active effects
        if self.game.shield: hud_text += " | [SHIELD]"
        if self.game.effects["speed"] > now: hud_text += " | [SPEED]"
        if self.game.effects["slow"] > now: hud_text += " | [SLOW]"
        hud_surface = f_s.render(hud_text, True, (255, 255, 255))
        screen.blit(hud_surface, (15, 15))

        pygame.display.update()
        
        # 4. FPS Control
        # Inside play_game() in main.py
        now = pygame.time.get_ticks()

# ... (drawing code) ...

# 4. FPS Control (The actual slowing logic)
        base_fps = self.game.fps

# Calculate modifiers
        speed_boost = 7 if self.game.effects["speed"] > now else 0
        slow_penalty = 5 if self.game.effects["slow"] > now else 0

# Apply modifiers to base_fps
        final_fps = base_fps + speed_boost - slow_penalty

# CRITICAL: Prevent the game from stopping or going backward
# A snake game feels "slow" at 4-5 FPS.
        if final_fps < 4:
            final_fps = 4

        pygame.time.Clock().tick(final_fps)

    def game_over_screen(self):
        screen.fill((0, 0, 0))
        t = f_l.render("GAME OVER", True, (255, 0, 0))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 100))
        if self.btn("RETRY", 150, 250, 120, 45, (0, 100, 0), (0, 150, 0)): self.game.reset(); self.state = "GAME"
        if self.btn("MENU", 330, 250, 120, 45, (70, 70, 70), (100, 100, 100)): self.game.reset(); self.state = "MENU"
        pygame.display.update()
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    def main_loop(self):
        while True:
            if self.state == "MENU": self.menu_screen()
            elif self.state == "GAME": self.play_game()
            elif self.state == "SET": self.settings_screen()
            elif self.state == "LEADER": self.leader_screen()
            elif self.state == "OVER": self.game_over_screen()

if __name__ == "__main__":
    Controller().main_loop()