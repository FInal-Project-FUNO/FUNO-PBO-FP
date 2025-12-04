"""
Deck class - Manages card collection and drawing
"""

from src.utils import *
from src.core import *
from src.core import Card

class Deck:
    """Manages a deck of cards"""
    
    def __init__(self):
        """Initialize a full UNO deck"""
        self.__cards = []
        self.__build_deck()
        self.shuffle()
    
    def __build_deck(self):
        """Build a complete UNO deck"""
        # Number cards (0: 1 per color, 1-9: 1 per color)
        for color in CARD_COLORS:
            for value in CARD_VALUES[0:]:
                self.__cards.append(Card(color, value))
        
        # Special cards (1 per color)
        for color in CARD_COLORS:
            self.__cards.append(Card(color, 'p2'))
            for special in SPECIAL_CARDS:
                self.__cards.append(Card(color, special))
        
        # Wild cards (2 of each)
        for color in WILD_CARDS:
            self.__cards.append(Card(color, color))
            self.__cards.append(Card(color, color))
    
    def shuffle(self):
        """Shuffle the deck"""
        shuffle_list(self.__cards)
    
    def draw(self):
        """
        Draw a card from the deck
        
        Returns:
            Card: The drawn card
            
        Raises:
            EmptyDeckError: If deck is empty
        """
        if self.is_empty():
            raise EmptyDeckError()
        return self.__cards.pop()
    
    def is_empty(self):
        """Check if deck is empty"""
        return len(self.__cards) == 0
    
    def cards_remaining(self):
        """Get number of cards remaining"""
        return len(self.__cards)
    
    def __len__(self):
        """Return deck size"""
        return len(self.__cards)
    
if __name__ == "__main__":
    deck1 = Deck()
    print(len(deck1))