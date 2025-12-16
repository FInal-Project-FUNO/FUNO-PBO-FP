from src.screen import *
from src.ui import *
from src.core.game_manager import GameManager

class ScreenManager:
    def __init__(self):
        self.current_screen = None
    
    def set_screen(self, screen_type):
        if screen_type == 'MENU':
            self.current_screen = MainMenu(self) # <--- Tambah ini
        elif screen_type == 'GAME':
            self.current_screen = GameScreen(self)
        # elif screen_type == 'DIFFICULTY':
        #     self.current_screen = DifficultyScreen(self)

    def handle_events(self, event):
        if self.current_screen:
            self.current_screen.handle_events(event)

    def update(self, delta_time):
        if self.current_screen:
            self.current_screen.update(delta_time)

    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)