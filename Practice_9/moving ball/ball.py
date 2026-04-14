import pygame

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_blue = True

    def handle_keys(self, width, height):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w] or pressed[pygame.K_UP]: self.y -= 20
        if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: self.y += 20
        if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: self.x -= 20
        if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: self.x += 20

        
        if self.x < self.radius: self.x = self.radius
        if self.x > width - self.radius: self.x = width - self.radius
        if self.y < self.radius: self.y = self.radius
        if self.y > height - self.radius: self.y = height - self.radius

    def toggle_color(self):
        self.is_blue = not self.is_blue

    def draw(self, screen):
        color = (0, 128, 255) if self.is_blue else (255, 100, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

