import pygame
from ball import Ball  

def main():
    pygame.init()
    width, height = 600, 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    
    
    my_ball = Ball(x=30, y=30, radius=20)
    
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                my_ball.toggle_color()

        
        my_ball.handle_keys(width, height)

        
        screen.fill((0, 0, 0))
        my_ball.draw(screen)
        
        pygame.display.flip()
        clock.tick(20)

    pygame.quit()

if __name__ == "__main__":
    main()