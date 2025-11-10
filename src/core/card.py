"""
Card class - Encapsulation of card data and behavior
"""

from src.utils import *
from src.core import *

class Card:
    """Represents a single UNO card"""
    
    def __init__(self, color, value):
        """
        Initialize a card
        
        Args:
            color: Card color (Red, Green, Blue, Yellow, Wild)
            value: Card value (0-9, Skip, Reverse, +2, Wild, Wild+4)
        """
        self.__color = color
        self.__value = value
        self.__points = CARD_POINTS.get(value, 0)
    
    # Getters (Encapsulation)
    @property
    def color(self):
        """Get card color"""
        return self.__color
    
    @property
    def value(self):
        """Get card value"""
        return self.__value
    
    @property
    def points(self):
        """Get card points"""
        return self.__points
    
    # Setters for Wild cards
    def set_color(self, new_color):
        """Set card color (for Wild cards)"""
        if self.__value in WILD_CARDS:
            self.__color = new_color
    
    def matches(self, other_card):
        """
        Check if this card matches another card
        
        Args:
            other_card: Another Card object
            
        Returns:
            bool: True if cards match
        """
        if self.__value in WILD_CARDS:
            return True
        if other_card.value in WILD_CARDS:
            return True
        return (self.__color == other_card.color or 
                self.__value == other_card.value)
    
    def is_special(self):
        """Check if card has special effect"""
        return self.__value in SPECIAL_CARDS + WILD_CARDS
    
    def __str__(self):
        """String representation"""
        return f"{self.__color} {self.__value}"
    
    def __repr__(self):
        """Developer representation"""
        return f"Card({self.__color}, {self.__value})"