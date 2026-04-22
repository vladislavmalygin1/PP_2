import pygame, sys
from pygame.locals import *
import random, time
import os

# Initializing 
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0      # Cars passed
COINS = 0      # Total coin weight collected
COIN_WEIGHTS = [1, 5, 10] # Different weight possibilities

# Setting up Fonts
font_small = pygame.font.SysFont("Verdana", 20)
game_over = pygame.font.SysFont("Verdana", 60).render("Game Over", True, BLACK)

# Display Setup
DISPLAYSURF = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Racer Game - Weighted Coins")

# Load Background
path = os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\road.png")
background = pygame.transform.scale(pygame.image.load(path), (SCREEN_WIDTH, SCREEN_HEIGHT))

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\white_car.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)  

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > 600):
            SCORE += 1 
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the base image
        self.original_image = pygame.image.load(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\coin.png")).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.weight = 1
        self.reset()

    def reset(self):
        """Randomly generates coin weight and position"""
        self.weight = random.choice(COIN_WEIGHTS)
        # Visual scaling: bigger coins have higher weight
        size = 20 + (self.weight * 2)
        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > 600:
            self.reset()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\imagess\red_car.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
        
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# Sprite Setup
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group(E1)
coins_group = pygame.sprite.Group(C1)
all_sprites = pygame.sprite.Group(P1, E1, C1)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0,0))
    
    # UI Text
    DISPLAYSURF.blit(font_small.render(f"Cars: {SCORE}", True, BLACK), (10,10))
    DISPLAYSURF.blit(font_small.render(f"Coins: {COINS}", True, BLACK), (SCREEN_WIDTH - 120, 10))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Coin Collection with Scaling Difficulty
    if pygame.sprite.spritecollide(P1, coins_group, False):
        old_coins = COINS
        COINS += C1.weight
        C1.reset()
        
        # Increase Enemy speed every 10 weight units
        if COINS // 10 > old_coins // 10:
            SPEED += 1

    # Collision Check
    if P1.rect.inflate(-20, -20).colliderect(E1.rect.inflate(-20, -20)):
        pygame.mixer.Sound(os.path.abspath(r"C:\Users\Bull\Desktop\PP_2\Practice1\Peactice_10\racer\sound\crash.mp3")).play()
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()        
         
    pygame.display.update()
    FramePerSec.tick(FPS)