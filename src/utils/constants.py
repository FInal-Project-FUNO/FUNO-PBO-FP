"""
Game constants and configuration settings
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Base folder for assets
ASSET_DIR = os.path.join(BASE_DIR, "assests")
# Card image paths
CARD_IMAGES = {
    "back": os.path.join(ASSET_DIR, "card","back_card.png"),
    "blue_0": os.path.join(ASSET_DIR, "card","blue_0.png"),
    "blue_1": os.path.join(ASSET_DIR, "card","blue_1.png"),
    "blue_2": os.path.join(ASSET_DIR, "card","blue_2.png"),
    "blue_3": os.path.join(ASSET_DIR, "card","blue_3.png"),
    "blue_4": os.path.join(ASSET_DIR, "card","blue_4.png"),
    "blue_5": os.path.join(ASSET_DIR, "card","blue_5.png"),
    "blue_6": os.path.join(ASSET_DIR, "card","blue_6.png"),
    "blue_7": os.path.join(ASSET_DIR, "card","blue_7.png"),
    "blue_8": os.path.join(ASSET_DIR, "card","blue_8.png"),
    "blue_9": os.path.join(ASSET_DIR, "card","blue_9.png"),
    "green_0": os.path.join(ASSET_DIR, "card","green_0.png"),
    "green_1": os.path.join(ASSET_DIR, "card","green_1.png"),
    "green_2": os.path.join(ASSET_DIR, "card","green_2.png"),
    "green_3": os.path.join(ASSET_DIR, "card","green_3.png"),
    "green_4": os.path.join(ASSET_DIR, "card","green_4.png"),
    "green_5": os.path.join(ASSET_DIR, "card","green_5.png"),
    "green_6": os.path.join(ASSET_DIR, "card","green_6.png"),
    "green_7": os.path.join(ASSET_DIR, "card","green_7.png"),
    "green_8": os.path.join(ASSET_DIR, "card","green_8.png"),
    "green_9": os.path.join(ASSET_DIR, "card","green_9.png"),
    "red_0": os.path.join(ASSET_DIR, "card","red_0.png"),
    "red_1": os.path.join(ASSET_DIR, "card","red_1.png"),
    "red_2": os.path.join(ASSET_DIR, "card","red_2.png"),
    "red_3": os.path.join(ASSET_DIR, "card","red_3.png"),
    "red_4": os.path.join(ASSET_DIR, "card","red_4.png"),
    "red_5": os.path.join(ASSET_DIR, "card","red_5.png"),
    "red_6": os.path.join(ASSET_DIR, "card","red_6.png"),
    "red_7": os.path.join(ASSET_DIR, "card","red_7.png"),
    "red_8": os.path.join(ASSET_DIR, "card","red_8.png"),
    "red_9": os.path.join(ASSET_DIR, "card","red_9.png"),
    "yell_0": os.path.join(ASSET_DIR, "card","yell_0.png"),
    "yell_1": os.path.join(ASSET_DIR, "card","yell_1.png"),
    "yell_2": os.path.join(ASSET_DIR, "card","yell_2.png"),
    "yell_3": os.path.join(ASSET_DIR, "card","yell_3.png"),
    "yell_4": os.path.join(ASSET_DIR, "card","yell_4.png"),
    "yell_5": os.path.join(ASSET_DIR, "card","yell_5.png"),
    "yell_6": os.path.join(ASSET_DIR, "card","yell_6.png"),
    "yell_7": os.path.join(ASSET_DIR, "card","yell_7.png"),
    "yell_8": os.path.join(ASSET_DIR, "card","yell_8.png"),
    "yell_9": os.path.join(ASSET_DIR, "card","yell_9.png"),
    "blue_p2": os.path.join(ASSET_DIR, "card","blue_p2.png"),
    "green_p2": os.path.join(ASSET_DIR, "card","green_p2.png"),
    "red_p2": os.path.join(ASSET_DIR, "card","red_p2.png"),
    "yell_p2": os.path.join(ASSET_DIR, "card","yell_p2.png"),
    "blue_reverse": os.path.join(ASSET_DIR, "card","blue_reverse.png"),
    "green_reverse": os.path.join(ASSET_DIR, "card","green_reverse.png"),
    "red_reverse": os.path.join(ASSET_DIR, "card","red_reverse.png"),
    "yell_reverse": os.path.join(ASSET_DIR, "card","yell_reverse.png"),
    "blue_skip": os.path.join(ASSET_DIR, "card","blue_skip.png"),
    "green_skip": os.path.join(ASSET_DIR, "card","green_skip.png"),
    "red_skip": os.path.join(ASSET_DIR, "card","red_skip.png"),
    "yell_skip": os.path.join(ASSET_DIR, "card","yell_skip.png"),
    "wild_wild": os.path.join(ASSET_DIR, "card","wildcard.png"), 
    "p4_p4": os.path.join(ASSET_DIR, "card","p4.png")
}

#Decks image
DECK_IMAGES = os.path.join(ASSET_DIR, "deck", "decks_funo.png")
DECK_FRAMES_COUNT = 5
MAX_DECK_SIZE = 60

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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
CARD_COLORS = ['red', 'green', 'blue', 'yell']
CARD_VALUES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SPECIAL_CARDS = ['skip', 'reverse', 'p2']
WILD_CARDS = ['wild', 'p4']

# Card points (bisa diganti pake int(value) ntaran)
CARD_POINTS = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
}

# Game settings
INITIAL_CARDS = 5
AI_DELAY = 2.5  # seconds