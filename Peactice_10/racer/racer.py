import pygame, sys
from pygame.locals import *
import random, time
import os

# Initializing 
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Other Variables
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0      # Cars passed
COINS = 0      # Coins collected

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Background Setup
path = os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\road.png")
original_image = pygame.image.load(path)
background = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Display Setup
DISPLAYSURF = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Racer Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\white_car.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 100)) # Resized to be thinner
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)  

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > 600):
            SCORE += 1 # Increase score when car passes
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Replace this path with your actual coin image path
        coin_path = os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\coin.png")
        self.image = pygame.image.load(coin_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        # Random spawn position
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > 600:
            # Reset coin to top if missed
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def reset(self):
        """Used when coin is collected to make it reappear at the top"""
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\red_car.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
        
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:        
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

# Setting up Sprites        
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Grouping
enemies = pygame.sprite.Group()
enemies.add(E1)

coins_group = pygame.sprite.Group()
coins_group.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Speed Increase Timer
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw Background
    DISPLAYSURF.blit(background, (0,0))
    
    # Render and Draw Scores
    scores = font_small.render(f"Cars: {SCORE}", True, BLACK)
    coin_count = font_small.render(f"Coins: {COINS}", True, BLACK)
    DISPLAYSURF.blit(scores, (10,10))
    DISPLAYSURF.blit(coin_count, (SCREEN_WIDTH - 100, 10)) # Top Right Corner

    # Update and Draw all entities
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Coin Collection Check
    # We check if player hits the coin
    if pygame.sprite.spritecollide(P1, coins_group, False):
        COINS += 1
        C1.reset() # Move coin back to top immediately

    # Collision Check (Enemy)
    # Using inflate(-20, -20) to make the hitbox smaller and fairer
    if P1.rect.inflate(-20, -20).colliderect(E1.rect.inflate(-20, -20)):
        pygame.mixer.Sound(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\sound\crash.mp3")).play()
        time.sleep(0.5)
                
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()
        
        for entity in all_sprites:
            entity.kill() 
        time.sleep(2)
        pygame.quit()
        sys.exit()        
         
    pygame.display.update()
    FramePerSec.tick(FPS)