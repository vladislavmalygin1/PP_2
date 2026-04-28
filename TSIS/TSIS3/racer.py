import pygame, random, time, os, sys
from pygame.locals import *

# Path to your assets
IMG_DIR = r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS3\assets"

def is_safe_distance(new_x, existing_sprites, min_dist=65):
    """Ensures objects do not spawn horizontally on top of each other."""
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

class Hazard(pygame.sprite.Sprite):
    def __init__(self, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "oil.png")), (40, 40))
        self.rect = self.image.get_rect(); self.reset()
    def reset(self):
        for _ in range(15):
            x = random.randint(60, 340)
            if is_safe_distance(x, self.all_sprites):
                self.rect.center = (x, random.randint(-400, -100)); return
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
    active_powerup, powerup_expiry, oil_timer = None, 0, 0

    all_objects = pygame.sprite.Group()
    E1 = Enemy(all_objects); all_objects.add(E1)
    C1 = Coin(all_objects); all_objects.add(C1)
    powerups, hazards = pygame.sprite.Group(), pygame.sprite.Group()

    player = pygame.sprite.Sprite()
    p_img = f"{settings.get('color', 'red')}_car.png"
    player.image = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, p_img)), (50, 90))
    player.rect = player.image.get_rect(center=(200, 500))

    while True:
        now = time.time()
        screen.blit(bg, (0,0)); distance += current_speed / 20
        total_score = int(distance) + (coins_collected * 10) + (score_cars * 5)

        if distance >= finish_line:
            pygame.mixer.music.stop(); return {"score": total_score + 1000, "distance": distance, "coins": coins_collected, "win": True}

        for event in pygame.event.get():
            if event.type == QUIT: pygame.mixer.music.stop(); return None

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and player.rect.left > 0: player.rect.move_ip(-7, 0)
        if keys[K_RIGHT] and player.rect.right < 400: player.rect.move_ip(7, 0)

        if E1.move(current_speed): score_cars += 1
        C1.rect.move_ip(0, current_speed)
        if C1.rect.top > 600: C1.reset()

        if active_powerup is None and len(powerups) == 0 and random.random() < 0.005:
            p = PowerUp(random.choice(["Shield", "Nitro"]), all_objects); powerups.add(p); all_objects.add(p)
        if random.random() < 0.008 and len(hazards) < 2:
            h = Hazard(all_objects); hazards.add(h); all_objects.add(h)

        # Fix: list-copy iteration to prevent crash at 1201m
        for obj in list(all_objects):
            if obj != E1 and obj != C1:
                obj.rect.move_ip(0, current_speed)
                if obj.rect.top > 600 or (isinstance(obj, PowerUp) and now - obj.spawn_time > 7): obj.kill()

        if player.rect.colliderect(C1.rect): coins_collected += C1.weight; C1.reset()
        
        h_hit = pygame.sprite.spritecollideany(player, hazards)
        if h_hit: active_powerup = None; current_speed = base_speed * 0.5; oil_timer = now + 2; h_hit.kill()

        p_hit = pygame.sprite.spritecollideany(player, powerups)
        if p_hit:
            active_powerup = p_hit.p_type; powerup_expiry = now + 6
            current_speed = base_speed + 5 if active_powerup == "Nitro" else base_speed; p_hit.kill()

        if active_powerup:
            if now > powerup_expiry:
                if active_powerup == "Nitro": current_speed = base_speed
                active_powerup = None
            elif active_powerup == "Nitro" and now > oil_timer: current_speed = base_speed + 5
        if now > oil_timer and active_powerup != "Nitro": current_speed = base_speed

        if player.rect.inflate(-15, -15).colliderect(E1.rect):
            if active_powerup == "Shield": active_powerup = None; E1.reset()
            else: 
                pygame.mixer.music.stop()
                if crash_sound: crash_sound.play()
                time.sleep(0.6)
                return {"score": total_score, "distance": distance, "coins": coins_collected, "win": False}

        all_objects.draw(screen); screen.blit(player.image, player.rect)
        
        # HUD: Drawn last to be on top
        hud_box = pygame.Surface((400, 60)); hud_box.set_alpha(150); hud_box.fill((255, 255, 255))
        screen.blit(hud_box, (0, 0))
        screen.blit(font.render(f"SCORE: {total_score}", True, (0,0,0)), (10, 5))
        screen.blit(font.render(f"COINS: {coins_collected}", True, (160, 100, 0)), (10, 30))
        screen.blit(font.render(f"FINISH: {max(0, finish_line-int(distance))}m", True, (200, 0, 0)), (240, 5))
        pygame.draw.rect(screen, (100, 100, 100), (240, 35, 150, 12))
        pygame.draw.rect(screen, (0, 200, 0), (240, 35, int(150 * min(1, distance/finish_line)), 12))
        if active_powerup:
            p_txt = font.render(f"{active_powerup.upper()}: {int(powerup_expiry - now)}s", True, (0, 0, 255))
            screen.blit(p_txt, (110, 15))

        pygame.display.update(); clock.tick(60)