import pygame
import math

def flood_fill(surface, start_pos, fill_color):
    """Fills a closed area using a stack-based flood fill algorithm."""
    width, height = surface.get_size()
    target_color = surface.get_at(start_pos)
    if target_color == fill_color: 
        return
    
    stack = [start_pos]
    while stack:
        x, y = stack.pop()
        if 0 <= x < width and 0 <= y < height:
            if surface.get_at((x, y)) == target_color:
                surface.set_at((x, y), fill_color)
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

def draw_line(surf, start, end, thickness, color):
    """Handles freehand drawing for the Pencil."""
    pygame.draw.line(surf, color, start, end, thickness)

def draw_eraser(surf, start, end, thickness):
    """Handles erasing by drawing white lines."""
    pygame.draw.line(surf, (255, 255, 255), start, end, thickness)

def draw_text(surf, text, pos, color, font):
    """Renders and blits text onto the surface."""
    text_surf = font.render(text, True, color)
    surf.blit(text_surf, pos)

def draw_shape(surf, mode, color, start, end, thickness):
    """Calculates and draws polygons/shapes with current thickness."""
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    width, height = abs(dx), abs(dy)
    t = thickness

    if mode == 'line':
        pygame.draw.line(surf, color, start, end, t)
    elif mode == 'rectangle':
        pygame.draw.rect(surf, color, (min(x1, x2), min(y1, y2), width, height), t)
    elif mode == 'square':
        side = max(width, height)
        sx = x1 if dx > 0 else x1 - side
        sy = y1 if dy > 0 else y1 - side
        pygame.draw.rect(surf, color, (sx, sy, side, side), t)
    elif mode == 'right_tri':
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surf, color, points, t)
    elif mode == 'eq_tri':
        h = int(width * (math.sqrt(3)/2))
        points = [(x1, y1), (x1 - width//2, y1 + h), (x1 + width//2, y1 + h)]
        pygame.draw.polygon(surf, color, points, t)
    elif mode == 'rhombus':
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        pygame.draw.polygon(surf, color, points, t)
    elif mode == 'circle':
        r = int(math.hypot(dx, dy))
        pygame.draw.circle(surf, color, start, r, t)