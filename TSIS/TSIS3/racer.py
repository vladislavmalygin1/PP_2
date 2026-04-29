import pygame, random, time, os, sys
from pygame.locals import *

# Path to your assets
IMG_DIR = r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS3\assets"

def is_safe_distance(new_x, existing_sprites, min_dist=65):
    """Ensures 60px+ horizontal distance between spawning objects to prevent blocking the road."""
    for s in existing_sprites:
        if s.rect.top < 150 and abs(new_x - s.rect.centerx) < min_dist:
            return False
    return True

class Enemy(pygame.sprite.Sprite):
    def __init__(self, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "white_car.png")), (50, 90))
        self.rect = self.image.get_rect(); self.reset()
    def reset(self):
        for _ in range(15):
            x = random.randint(60, 340)
            if is_safe_distance(x, self.all_sprites):
                self.rect.center = (x, -100); return
        self.rect.center = (random.randint(60, 340), -100)
    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600: self.reset(); return True
        return False

class Barrier(pygame.sprite.Sprite):
    def __init__(self, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "barrier.png")), (60, 40))
        self.rect = self.image.get_rect(); self.reset()
    def reset(self):
        for _ in range(15):
            x = random.randint(60, 340)
            if is_safe_distance(x, self.all_sprites):
                self.rect.center = (x, -100); return
        self.rect.center = (random.randint(60, 340), -100)

class Coin(pygame.sprite.Sprite):
    def __init__(self, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.raw = pygame.image.load(os.path.join(IMG_DIR, "coin.png"))
        self.reset()
    def reset(self):
        self.weight = random.choice([1, 5, 10])
        sz = 24 + (self.weight * 2)
        self.image = pygame.transform.scale(self.raw, (sz, sz))
        self.rect = self.image.get_rect()
        for _ in range(15):
            x = random.randint(60, 340)
            if is_safe_distance(x, self.all_sprites):
                self.rect.center = (x, random.randint(-500, -100)); return
        self.rect.center = (random.randint(60, 340), -200)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, p_type, all_sprites):
        super().__init__()
        self.p_type, self.all_sprites = p_type, all_sprites
        img = "shield.png" if p_type == "Shield" else "nitro.png"
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, img)), (30, 30))
        self.rect = self.image.get_rect(); self.spawn_time = time.time(); self.reset()
    def reset(self):
        for _ in range(15):
            x = random.randint(60, 340)
            if is_safe_distance(x, self.all_sprites):
                self.rect.center = (x, random.randint(-300, -100)); return
        self.rect.center = (random.randint(60, 340), -150)

def game_over_screen(screen, results):
    from ui import Button
    f_lg = pygame.font.SysFont("Verdana", 40, bold=True)
    f_md = pygame.font.SysFont("Verdana", 20)
    overlay = pygame.Surface((400, 600)); overlay.set_alpha(210); overlay.fill((0, 0, 0))
    while True:
        screen.blit(overlay, (0,0))
        txt = "VICTORY!" if results['win'] else "GAME OVER"
        clr = (100, 255, 100) if results['win'] else (255, 50, 50)
        screen.blit(f_lg.render(txt, True, clr), (85, 100))
        screen.blit(f_md.render(f"Final Score: {results['score']}", True, (255,255,255)), (110, 200))
        b_retry = Button("RETRY", 100, 380, 200, 50, (100, 200, 100), (150, 250, 150))
        b_menu  = Button("MENU", 100, 450, 200, 50, (100, 100, 250), (150, 150, 250))
        for event in pygame.event.get():
            if b_retry.is_clicked(event): return "retry"
            if b_menu.is_clicked(event): return "menu"
            if event.type == QUIT: pygame.quit(); sys.exit()
        b_retry.draw(screen); b_menu.draw(screen); pygame.display.update()

def play_game(screen, settings):
    pygame.mixer.init()
    if settings.get('music', True):
        try:
            pygame.mixer.music.load(os.path.join(IMG_DIR, "music_2.mp3"))
            pygame.mixer.music.play(-1)
        except: pass
    
    crash_sound = None
    try: crash_sound = pygame.mixer.Sound(os.path.join(IMG_DIR, "crash.mp3"))
    except: pass

    clock = pygame.time.Clock(); font = pygame.font.SysFont("Verdana", 18, bold=True)
    bg = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "road.png")), (400, 600))
    
    base_speed = 4 + (settings.get('difficulty', 1) * 2)
    current_speed = base_speed
    finish_line, score_cars, coins_collected, distance = 1500, 0, 0, 0
    active_powerup, powerup_expiry = None, 0

    all_objects = pygame.sprite.Group()
    E1 = Enemy(all_objects); all_objects.add(E1)
    B1 = Barrier(all_objects); all_objects.add(B1)
    C1 = Coin(all_objects); all_objects.add(C1)
    powerups = pygame.sprite.Group()

    player = pygame.sprite.Sprite()
    p_img = f"{settings.get('color', 'red')}_car.png"
    player.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, p_img)), (50, 90))
    player.rect = player.image.get_rect(center=(200, 500))

    while True:
        now = time.time()
        screen.blit(bg, (0,0)); distance += current_speed / 20
        total_score = int(distance) + (coins_collected * 10) + (score_cars * 5)

        if distance >= finish_line:
            pygame.mixer.music.stop()
            return {"score": total_score + 1000, "distance": distance, "win": True}

        for event in pygame.event.get():
            if event.type == QUIT: pygame.mixer.music.stop(); return None

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and player.rect.left > 0: player.rect.move_ip(-7, 0)
        if keys[K_RIGHT] and player.rect.right < 400: player.rect.move_ip(7, 0)

        # Move Core Sprites
        if E1.move(current_speed): score_cars += 1
        B1.rect.move_ip(0, current_speed)
        if B1.rect.top > 600: B1.reset()
        C1.rect.move_ip(0, current_speed)
        if C1.rect.top > 600: C1.reset()

        # Spawn PowerUps
        if active_powerup is None and len(powerups) == 0 and random.random() < 0.005:
            p = PowerUp(random.choice(["Shield", "Nitro"]), all_objects); powerups.add(p); all_objects.add(p)

        # Move dynamic objects using list-copy to avoid modification errors
        for obj in list(all_objects):
            if obj not in [E1, B1, C1]:
                obj.rect.move_ip(0, current_speed)
                if obj.rect.top > 600 or (isinstance(obj, PowerUp) and now - obj.spawn_time > 7): obj.kill()

        if player.rect.colliderect(C1.rect): coins_collected += C1.weight; C1.reset()
        
        # Collision with Obstacles (Enemy or Barrier)
        obstacle_hit = player.rect.inflate(-15, -15).colliderect(E1.rect) or \
                       player.rect.inflate(-10, -10).colliderect(B1.rect)

        if obstacle_hit:
            if active_powerup == "Shield":
                active_powerup = None # Consume shield
                if player.rect.colliderect(E1.rect): E1.reset()
                else: B1.reset()
            else: 
                pygame.mixer.music.stop()
                if crash_sound: crash_sound.play()
                time.sleep(0.6)
                return {"score": total_score, "distance": distance, "win": False}

        # Collect PowerUps
        p_hit = pygame.sprite.spritecollideany(player, powerups)
        if p_hit:
            active_powerup = p_hit.p_type
            powerup_expiry = now + 6
            current_speed = base_speed + 5 if active_powerup == "Nitro" else base_speed
            p_hit.kill()

        # Handle Expiration
        if active_powerup and now > powerup_expiry:
            if active_powerup == "Nitro": current_speed = base_speed
            active_powerup = None

        all_objects.draw(screen); screen.blit(player.image, player.rect)
        
        # --- HUD ---
        hud_box = pygame.Surface((400, 60)); hud_box.set_alpha(150); hud_box.fill((255, 255, 255))
        screen.blit(hud_box, (0, 0))
        screen.blit(font.render(f"SCORE: {total_score}", True, (0,0,0)), (10, 5))
        screen.blit(font.render(f"COINS: {coins_collected}", True, (160, 100, 0)), (10, 30))
        screen.blit(font.render(f"FINISH: {max(0, finish_line-int(distance))}m", True, (200, 0, 0)), (240, 5))
        
        # Progress Bar
        pygame.draw.rect(screen, (100, 100, 100), (240, 35, 150, 12))
        pygame.draw.rect(screen, (0, 200, 0), (240, 35, int(150 * min(1, distance/finish_line)), 12))
        
        # PowerUp Text (FIXED)
        if active_powerup:
            time_left = max(0, int(powerup_expiry - now))
            p_clr = (0, 0, 255) if active_powerup == "Shield" else (0, 150, 0)
            p_txt = font.render(f"{active_powerup.upper()}: {time_left}s", True, p_clr)
            screen.blit(p_txt, (110, 15))

        pygame.display.update(); clock.tick(60)