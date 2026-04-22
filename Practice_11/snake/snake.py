import pygame
import random
import sys

pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
WHITE, RED, GREEN, BLACK, GOLD = (255,255,255), (213,50,80), (0,255,0), (0,0,0), (255,215,0)

# Food Data: Weight and lifespan in milliseconds
FOOD_TYPES = [
    {"weight": 1, "color": RED, "timer": 10000},  # Normal
    {"weight": 3, "color": GOLD, "timer": 5000}   # Bonus (disappears faster)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("bahnschrift", 25)

def generate_food(snake_list):
    """Generates weighted food with a timestamp"""
    ftype = random.choice(FOOD_TYPES)
    while True:
        fx = round(random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        fy = round(random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        if [fx, fy] not in snake_list:
            return [fx, fy], ftype, pygame.time.get_ticks()

def game_loop():
    fps, score, level = 10, 0, 1
    x, y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
    x_change, y_change = 0, 0
    snake_list = []
    snake_len = 1
    
    # Initial food spawn
    food_pos, food_data, spawn_time = generate_food(snake_list)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0: x_change, y_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and x_change == 0: x_change, y_change = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and y_change == 0: y_change, x_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_DOWN and y_change == 0: y_change, x_change = BLOCK_SIZE, 0

        # Check if food expired
        if pygame.time.get_ticks() - spawn_time > food_data["timer"]:
            food_pos, food_data, spawn_time = generate_food(snake_list)

        x += x_change; y += y_change
        if x >= SCREEN_WIDTH or x < 0 or y >= SCREEN_HEIGHT or y < 0: break # Wall collision

        screen.fill(BLACK)
        pygame.draw.rect(screen, food_data["color"], [food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE])

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_len: del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head: return # Self collision

        for segment in snake_list:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])

        # Food Collision
        if x == food_pos[0] and y == food_pos[1]:
            score += food_data["weight"]
            snake_len += 1
            if score // 5 > level: # Level up every 5 points
                level += 1; fps += 2
            food_pos, food_data, spawn_time = generate_food(snake_list)

        val = font_style.render(f"Score: {score} Level: {level}", True, WHITE)
        screen.blit(val, [10, 10])
        pygame.display.update()
        clock.tick(fps)

game_loop()