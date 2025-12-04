from src.screen.game_screen import GameScreen
# from src.screens.menu_screen import MenuScreen

class ScreenManager:
    def __init__(self):
        self.current_screen = None
    
    def set_screen(self, screen_type):
        if screen_type == 'GAME':
            self.current_screen = GameScreen(self)
        # elif screen_type == 'MENU':
        #     self.current_screen = MenuScreen(self)

    def handle_events(self, event):
        if self.current_screen:
            self.current_screen.handle_events(event)

    def update(self, delta_time):
        if self.current_screen:
            self.current_screen.update(delta_time)

    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)