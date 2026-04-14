import pygame
import random
import sys

# Initializing Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20

# Colors
WHITE = (255, 255, 255)
RED   = (213, 50, 80)   # Food
GREEN = (0, 255, 0)     # Snake
BLACK = (0, 0, 0)       # Background

# Game Variables
fps = 10
score = 0
level = 1
food_per_level = 3

# Display Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game - Level Up')
clock = pygame.time.Clock()

font_style = pygame.font.SysFont("bahnschrift", 25)

def show_score(score, level):
    """Displays current score and level on the screen"""
    value = font_style.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(value, [10, 10])

def generate_food(snake_list):
    """Generates food at a random position that isn't on the snake"""
    while True:
        food_x = round(random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        food_y = round(random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        
        # Check if food spawned inside the snake body
        if [food_x, food_y] not in snake_list:
            return food_x, food_y

def game_loop():
    global fps, score, level

    game_over = False
    
    # Starting position (Middle of screen)
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    
    # Movement variables
    x_change = 0
    y_change = 0

    # Snake body structure
    snake_list = []
    length_of_snake = 1

    # Initial food position
    food_x, food_y = generate_food(snake_list)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle direction changes
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -BLOCK_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = BLOCK_SIZE
                    x_change = 0

        # --- COLLISION: WALLS ---
        if x >= SCREEN_WIDTH or x < 0 or y >= SCREEN_HEIGHT or y < 0:
            game_over = True

        x += x_change
        y += y_change
        screen.fill(BLACK)

        # Draw Food
        pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])

        # Manage Snake Body
        snake_head = [x, y]
        snake_list.append(snake_head)
        
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # --- COLLISION: SELF ---
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over = True

        # Draw Snake
        for segment in snake_list:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])

        show_score(score, level)
        pygame.display.update()

        # --- COLLISION: FOOD ---
        if x == food_x and y == food_y:
            food_x, food_y = generate_food(snake_list)
            length_of_snake += 1
            score += 1

            # --- LEVEL UP SYSTEM ---
            # Every 3 foods, increase level and speed
            if score % food_per_level == 0:
                level += 1
                fps += 2  # Increase speed by 2 frames per level

        clock.tick(fps)

    # Simple Game Over screen
    screen.fill(RED)
    msg = font_style.render("Game Over! Final Score: " + str(score), True, WHITE)
    screen.blit(msg, [SCREEN_WIDTH / 6, SCREEN_HEIGHT / 3])
    pygame.display.update()
    pygame.time.delay(2000)

game_loop()