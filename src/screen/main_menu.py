import pygame
import sys
import os
from .base import BaseScreen
from ..utils.constants import *
from ..ui.components import Button

class MainMenu(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_title = pygame.font.Font(FONT_PATH, 60)
        self.font_button = pygame.font.Font(FONT_PATH, 30)
        
        # Posisi Tengah Layar
        center_x = SCREEN_WIDTH // 2
        start_y = 250
        btn_width = 200
        btn_height = 50
        gap = 70

        # Inisialisasi Tombol dengan Callback Action
        self.buttons = [
            Button(center_x - btn_width//2, start_y, btn_width, btn_height, 
                   "Play", self.font_button, self.action_play),
            
            Button(center_x - btn_width//2, start_y + gap, btn_width, btn_height, 
                   "Difficulty", self.font_button, self.action_difficulty),
            
            Button(center_x - btn_width//2, start_y + gap*2, btn_width, btn_height, 
                   "Exit", self.font_button, self.action_exit)
        ]

    # --- Actions / Callbacks ---
    def action_play(self):
        print("Pindah ke Game Screen")
        self.manager.set_screen('GAME')

    def action_difficulty(self):
        print("Pindah ke Difficulty Screen")
        # Nanti diimplementasikan: self.manager.set_screen('DIFFICULTY')
        pass 

    def action_exit(self):
        pygame.quit()
        sys.exit()

    # --- Override Methods ---
    def handle_events(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, delta_time):
        pass # Bisa ditambah animasi background nanti

    def draw(self, surface):
        # surface.fill(COLOR_BG) # Background
        menu = pygame.image.load(MENU_PATH).convert()
        surface.blit(menu, (0, 0))

        # 1. Draw Title
        title_path = os.path.join("assests", "ui", "title.png")
        title = pygame.image.load(title_path)
        surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 75))
        
        # 2. Draw Buttons
        for btn in self.buttons:
            btn.draw(surface)