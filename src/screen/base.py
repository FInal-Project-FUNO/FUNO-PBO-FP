class BaseScreen:
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, event):
        pass

    def update(self, delta_time):
        pass

    def draw(self, surface):
        pass