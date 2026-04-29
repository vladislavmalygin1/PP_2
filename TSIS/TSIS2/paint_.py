import pygame
import datetime
import os
import tools

# --- CONFIGURATION ---
ASSETS_PATH = r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS2\assets"

class ToolButton:
    def __init__(self, x, y, mode_name, icon_filename, is_size=False, size_val=2):
        self.rect = pygame.Rect(x, y, 35, 35)
        self.mode = mode_name
        self.is_size = is_size
        self.size_val = size_val
        
        path = os.path.join(ASSETS_PATH, icon_filename)
        try:
            self.icon = pygame.image.load(path)
            self.icon = pygame.transform.scale(self.icon, (30, 30))
        except:
            self.icon = None

    def draw(self, screen, current_mode, current_thickness):
        # Determine if this button should be highlighted
        active = (current_mode == self.mode) if not self.is_size else (current_thickness == self.size_val)
        bg = (120, 120, 120) if active else (60, 60, 60)
        
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 1)
        
        if self.icon:
            screen.blit(self.icon, (self.rect.x + 2, self.rect.y + 2))
        else:
            # Fallback text
            f = pygame.font.SysFont("Arial", 12)
            lbl = self.mode[:3] if not self.is_size else str(self.size_val)
            screen.blit(f.render(lbl, True, (255,255,255)), (self.rect.x+5, self.rect.y+10))

def draw_ui(screen, color, buttons, mode, thickness):
    # 1. Rainbow Palette
    for i in range(255):
        h = pygame.Color(0)
        h.hsva = (i * 360 / 255, 100, 100, 100)
        pygame.draw.rect(screen, h, (770, i * 2, 30, 2))
    pygame.draw.rect(screen, (255, 255, 255), (770, 510, 30, 40))
    pygame.draw.rect(screen, (0, 0, 0), (770, 550, 30, 40))
    pygame.draw.rect(screen, color, (770, 0, 30, 20)) # Current color indicator

    # 2. Draw Tool Buttons
    for b in buttons:
        b.draw(screen, mode, thickness)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TSIS2 Paint - Final")
    
    canvas = pygame.Surface((725, 600))
    canvas.fill((255, 255, 255))
    clock = pygame.time.Clock()
    
    # Define UI Buttons
    buttons = [
        ToolButton(730, 30, 'pencil', 'pencil.png'),
        ToolButton(730, 70, 'eraser', 'eraser.png'),
        ToolButton(730, 110, 'line', 'line.png'),
        ToolButton(730, 150, 'rectangle', 'rectangle.png'),
        ToolButton(730, 190, 'square', 'square.png'),
        ToolButton(730, 230, 'right_tri', 'r_triangle.png'),
        ToolButton(730, 270, 'eq_tri', 'eq_triangle.png'),
        ToolButton(730, 310, 'rhombus', 'rhombus.png'),
        ToolButton(730, 350, 'circle', 'circle.png'),
        ToolButton(730, 390, 'fill', 'fill.png'),
        ToolButton(730, 430, 'text', 'text.png'),
        # Size Buttons (Optional: can use size1.png, size2.png etc if you have them)
        ToolButton(730, 480, '', 'size1.png', True, 2),
        ToolButton(730, 520, '', 'size2.png', True, 5),
        ToolButton(730, 560, '', 'size3.png', True, 12),
    ]

    color, mode, thickness = (0, 0, 0), 'pencil', 2
    drawing = False
    start_pos = last_pos = None
    font = pygame.font.SysFont("Arial", 24)
    typing, text_buffer, text_pos = False, "", (0,0)

    while True:
        screen.fill((45, 45, 45))
        draw_ui(screen, color, buttons, mode, thickness)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] >= 770: # Clicked Palette
                    color = screen.get_at(event.pos)
                elif 725 <= event.pos[0] < 770: # Clicked Toolbar
                    for b in buttons:
                        if b.rect.collidepoint(event.pos):
                            if b.is_size: thickness = b.size_val
                            else: 
                                mode = b.mode
                                typing = False
                else: # Clicked Canvas
                    if mode == 'fill': tools.flood_fill(canvas, event.pos, color)
                    elif mode == 'text':
                        typing, text_pos, text_buffer = True, event.pos, ""
                    else:
                        drawing = True
                        start_pos = last_pos = event.pos

            if event.type == pygame.KEYDOWN:
                if typing:
                    if event.key == pygame.K_RETURN:
                        tools.draw_text(canvas, text_buffer, text_pos, color, font)
                        typing = False
                    elif event.key == pygame.K_ESCAPE: typing = False
                    elif event.key == pygame.K_BACKSPACE: text_buffer = text_buffer[:-1]
                    else: text_buffer += event.unicode
                else:
                    # Save Shortcut
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if not os.path.exists(ASSETS_PATH): os.makedirs(ASSETS_PATH)
                        fn = f"save_{datetime.datetime.now().strftime('%H%M%S')}.png"
                        pygame.image.save(canvas, os.path.join(ASSETS_PATH, fn))

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
        if drawing and mode not in ['pencil', 'eraser', 'fill', 'text']:
            tools.draw_shape(screen, mode, color, start_pos, pygame.mouse.get_pos(), thickness)
        if typing: tools.draw_text(screen, text_buffer + "|", text_pos, color, font)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()