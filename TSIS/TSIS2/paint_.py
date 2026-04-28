import pygame
import datetime
import os
import tools

def draw_ui(screen, color):
    # Palette
    for i in range(255):
        hue = pygame.Color(0)
        hue.hsva = (i * 360 / 255, 100, 100, 100)
        pygame.draw.rect(screen, hue, (770, i * 2, 30, 2))
    pygame.draw.rect(screen, (255, 255, 255), (770, 510, 30, 40))
    pygame.draw.rect(screen, (0, 0, 0), (770, 550, 30, 40))
    # Current color
    pygame.draw.rect(screen, color, (770, 0, 30, 20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Paint Pro")
    
    canvas = pygame.Surface((760, 600))
    canvas.fill((255, 255, 255))
    clock = pygame.time.Clock()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

    # State
    color = (0, 0, 0)
    mode = 'pencil'
    thickness = 2
    drawing = False
    start_pos = last_pos = None
    
    # Text state
    font = pygame.font.SysFont("Arial", 24)
    typing = False
    text_buffer = ""
    text_pos = (0, 0)

    while True:
        screen.fill((40, 40, 40))
        draw_ui(screen, color)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] >= 770:
                    color = screen.get_at(event.pos)
                else:
                    if mode == 'fill':
                        tools.flood_fill(canvas, event.pos, color)
                    elif mode == 'text':
                        typing = True
                        text_pos = event.pos
                        text_buffer = ""
                    else:
                        drawing = True
                        start_pos = last_pos = event.pos

            if event.type == pygame.KEYDOWN:
                # Text Tool typing logic
                if typing:
                    if event.key == pygame.K_RETURN:
                        tools.draw_text(canvas, text_buffer, text_pos, color, font)
                        typing = False
                    elif event.key == pygame.K_ESCAPE:
                        typing = False # Cancel typing, nothing drawn
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        text_buffer += event.unicode
                else:
                    # Normal mode/size selection
                    if event.key == pygame.K_p: mode = 'pencil'
                    if event.key == pygame.K_e: mode = 'eraser'
                    if event.key == pygame.K_r: mode = 'rectangle'
                    if event.key == pygame.K_s: mode = 'square'
                    if event.key == pygame.K_t: mode = 'right_tri'
                    if event.key == pygame.K_q: mode = 'eq_tri'
                    if event.key == pygame.K_h: mode = 'rhombus'
                    if event.key == pygame.K_c: mode = 'circle'
                    if event.key == pygame.K_f: mode = 'fill'
                    if event.key == pygame.K_x: mode = 'text'
                    if event.key == pygame.K_l: mode = 'line'

                    if event.key == pygame.K_1: thickness = 2
                    if event.key == pygame.K_2: thickness = 5
                    if event.key == pygame.K_3: thickness = 12

                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)
                        fname = f"save_{datetime.datetime.now().strftime('%H%M%S')}.png"
                        pygame.image.save(canvas, os.path.join(ASSETS_DIR, fname))

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    if mode not in ['pencil', 'eraser']:
                        tools.draw_shape(canvas, mode, color, start_pos, event.pos, thickness)
                    drawing = False

            if event.type == pygame.MOUSEMOTION and drawing:
                if mode == 'pencil':
                    tools.draw_line(canvas, last_pos, event.pos, thickness, color)
                    last_pos = event.pos
                elif mode == 'eraser':
                    tools.draw_eraser(canvas, last_pos, event.pos, thickness)
                    last_pos = event.pos

        screen.blit(canvas, (0, 0))
        
        # Previews
        if drawing and mode not in ['pencil', 'eraser', 'fill', 'text']:
            tools.draw_shape(screen, mode, color, start_pos, pygame.mouse.get_pos(), thickness)
        
        if typing:
            tools.draw_text(screen, text_buffer + "|", text_pos, color, font)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()