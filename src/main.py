# src/main.py
import pygame
import sys
from .utils.constants import *
from .screen_manager import ScreenManager
from .ui.deck_animation import * 

# 1. Setup Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FUNO - Fast UNO Game")
clock = pygame.time.Clock()

def main():
    # 2. Setup Screen Manager
    manager = ScreenManager()
    manager.set_screen('MENU') # Mulai dari Menu (jika sudah siap) atau 'GAME'

    # 3. Main Loop
    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0 # Hitung delta time (detik)

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Oper event ke screen aktif
            manager.handle_events(event)

        # Update & Draw Screen Aktif
        manager.update(delta_time)
        manager.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()