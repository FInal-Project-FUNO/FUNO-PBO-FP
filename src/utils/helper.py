"""
Helper functions for the game
"""
import random
from .constants import *

def shuffle_list(items):
    """Shuffle a list in place"""
    random.shuffle(items)
    return items

def get_color_rgb(color_name):
    """Convert color name to RGB tuple"""
    color_map = {
        'Red': COLOR_RED,
        'Green': COLOR_GREEN,
        'Blue': COLOR_BLUE,
        'Yellow': COLOR_YELLOW,
        'Wild': COLOR_BLACK
    }
    return color_map.get(color_name, COLOR_GRAY)