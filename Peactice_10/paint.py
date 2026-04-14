import pygame
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))
    
    clock = pygame.time.Clock()
    
    radius = 15
    color = (0, 0, 255) 
    mode = 'brush' 
    
    drawing = False
    start_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                
                if event.key == pygame.K_b: mode = 'brush'
                if event.key == pygame.K_r: mode = 'rectangle'
                if event.key == pygame.K_c: mode = 'circle'
                if event.key == pygame.K_e: mode = 'eraser'
                if event.key == pygame.K_z: canvas.fill((0, 0, 0))

                if event.key == pygame.K_1: color = (255, 0, 0) 
                if event.key == pygame.K_2: color = (0, 255, 0) 
                if event.key == pygame.K_3: color = (0, 0, 255) 
                if event.key == pygame.K_4: color = (255, 255, 0)
                if event.key == pygame.K_5: color = (255, 0, 255)
            
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                if mode == 'brush' or mode == 'eraser':
                    
                    if mode == 'eraser':
                        draw_color = (0,0,0)  
                    else:
                        draw_color = color
                    pygame.draw.circle(canvas, draw_color, event.pos, radius)

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    
                    end_pos = event.pos
                    draw_shape(canvas, mode, color, start_pos, end_pos, radius)
                    drawing = False

            if event.type == pygame.MOUSEMOTION:
                if drawing and (mode == 'brush' or mode == 'eraser'):
                    
                    draw_color = (0,0,0) if mode == 'eraser' else color
                    pygame.draw.circle(canvas, draw_color, event.pos, radius)
        screen.blit(canvas, (0, 0))

        if drawing and mode in ['rectangle', 'circle']:
            current_pos = pygame.mouse.get_pos()
            draw_shape(screen, mode, color, start_pos, current_pos, radius, preview=True)

        pygame.display.flip()
        clock.tick(120)

def draw_shape(surface, mode, color, start, end, radius, preview=False):
    x1, y1 = start
    x2, y2 = end
    
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    top_left = (min(x1, x2), min(y1, y2))

    if mode == 'rectangle':
        pygame.draw.rect(surface, color, (top_left[0], top_left[1], width, height), 1 if preview else 0)
    
    elif mode == 'circle':
        dist = int(math.hypot(x2 - x1, y2 - y1))
        pygame.draw.circle(surface, color, start, dist, 2 if preview else 0)

if __name__ == "__main__":
    main()