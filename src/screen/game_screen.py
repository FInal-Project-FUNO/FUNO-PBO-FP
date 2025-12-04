import pygame
from .base import BaseScreen
from src.core.game_manager import GameManager
from src.utils.constants import *
# Import fungsi draw visual lain jika ditaruh di UI folder

class GameScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        self.game_logic = GameManager() # Logika game ada di sini
        # Load assets di sini agar rapi

    def handle_events(self, event):
        # Pindahkan logika MOUSEBUTTONDOWN dari main.py ke sini
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Logika klik kartu...
            pass

    def update(self, delta_time):
        # Update AI, animasi, dll
        self.game_logic.update_ai()

    def draw(self, surface):
        surface.fill(COLOR_DARK_GREEN)
        
        # Panggil fungsi visualisasi di sini
        # self.draw_deck(surface)
        # self.draw_player_cards(surface)
        # dst...