"""
Game constants and configuration settings
"""

import os

# Base folder for assets
ASSET_DIR = r"E:\Coding\Python\PBO\FUNO-PBO-FP\assests\card"

# Card image paths
CARD_IMAGES = {
    "back": os.path.join(ASSET_DIR, "back_card_funo.png"),
    "blue_0": os.path.join(ASSET_DIR, "blue_0.png"),
    "blue_1": os.path.join(ASSET_DIR, "blue_1.png"),
    "green_0": os.path.join(ASSET_DIR, "green_0.png"),
    "green_1": os.path.join(ASSET_DIR, "green_1.png"),
    "red_0": os.path.join(ASSET_DIR, "red_0.png"),
    "red_1": os.path.join(ASSET_DIR, "red_1.png"),
    "yell_0": os.path.join(ASSET_DIR, "yell_0.png"),
    "yell_1": os.path.join(ASSET_DIR, "yell_1.png"),
}

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GREEN = (0, 100, 0)

# Card settings
CARD_WIDTH = 128
CARD_HEIGHT = 128
CARD_COLORS = ['Red', 'Green', 'Blue', 'Yellow']
CARD_VALUES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SPECIAL_CARDS = ['Skip', 'Reverse', '+2']
WILD_CARDS = ['Wild', 'Wild+4']

# Card points
CARD_POINTS = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'Skip': 20, 'Reverse': 20, '+2': 20,
    'Wild': 50, 'Wild+4': 50
}

# Game settings
INITIAL_CARDS = 7
AI_DELAY = 10.0  # seconds