import pygame
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    canvas = pygame.Surface((800, 600))
    clock = pygame.time.Clock()
    
    color = (0, 0, 255) 
    mode = 'brush' # brush, eraser, rectangle, circle, square, right_tri, eq_tri, rhombus
    drawing = False
    start_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b: mode = 'brush'
                if event.key == pygame.K_e: mode = 'eraser'
                if event.key == pygame.K_r: mode = 'rectangle'
                if event.key == pygame.K_c: mode = 'circle'
                if event.key == pygame.K_s: mode = 'square' #
                if event.key == pygame.K_t: mode = 'right_tri' #
                if event.key == pygame.K_q: mode = 'eq_tri' #
                if event.key == pygame.K_h: mode = 'rhombus' #
                if event.key == pygame.K_1: color = (255, 0, 0) 
                if event.key == pygame.K_2: color = (0, 255, 0) 
                if event.key == pygame.K_3: color = (0, 0, 255) 
                if event.key == pygame.K_4: color = (255, 255, 0)
                if event.key == pygame.K_5: color = (255, 0, 255)
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                if mode in ['brush', 'eraser']:
                    draw_color = (0,0,0) if mode == 'eraser' else color
                    pygame.draw.circle(canvas, draw_color, event.pos, 10)

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    draw_shape(canvas, mode, color, start_pos, event.pos, preview=False)
                    drawing = False

            if event.type == pygame.MOUSEMOTION and drawing and mode in ['brush', 'eraser']:
                draw_color = (0,0,0) if mode == 'eraser' else color
                pygame.draw.circle(canvas, draw_color, event.pos, 10)

        screen.blit(canvas, (0, 0))
        if drawing and mode not in ['brush', 'eraser']:
            draw_shape(screen, mode, color, start_pos, pygame.mouse.get_pos(), preview=True)

        pygame.display.flip()
        clock.tick(60)

def draw_shape(surf, mode, color, start, end, preview=False):
    """Calculates and draws polygons for advanced shapes"""
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    width, height = abs(dx), abs(dy)

    if mode == 'rectangle':
        pygame.draw.rect(surf, color, (min(x1, x2), min(y1, y2), width, height), 2 if preview else 0)
    
    elif mode == 'square': #
        side = max(width, height)
        sx = x1 if dx > 0 else x1 - side
        sy = y1 if dy > 0 else y1 - side
        pygame.draw.rect(surf, color, (sx, sy, side, side), 2 if preview else 0)

    elif mode == 'right_tri': #
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surf, color, points, 2 if preview else 0)

    elif mode == 'eq_tri': #
        # h = side * sin(60)
        h = int(width * (math.sqrt(3)/2))
        points = [(x1, y1), (x1 - width//2, y1 + h), (x1 + width//2, y1 + h)]
        pygame.draw.polygon(surf, color, points, 2 if preview else 0)

    elif mode == 'rhombus': #
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        pygame.draw.polygon(surf, color, points, 2 if preview else 0)

    elif mode == 'circle':
        r = int(math.hypot(dx, dy))
        pygame.draw.circle(surf, color, start, r, 2 if preview else 0)

if __name__ == "__main__":
    main()