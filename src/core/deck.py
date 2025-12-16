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
        
        # Special cards (1 per color except plus2 which has 2)
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
    
    def draw_valid(self, condition_func):
        """
        Mencari dan mengambil kartu pertama yang memenuhi syarat (condition_func).
        Kartu diambil langsung dari tumpukan tanpa perlu re-shuffle.
        
        Args:
            condition_func: Fungsi yang menerima object Card dan me-return True/False
        """
        # Kita iterasi dari belakang (atas tumpukan) agar urutan deck tetap terjaga
        # range(start, stop, step) -> dari index terakhir sampai 0
        for i in range(len(self.__cards) - 1, -1, -1):
            card = self.__cards[i]
            
            # Cek apakah kartu ini memenuhi syarat yang diminta GameManager
            if condition_func(card):
                # Hapus dari list dan kembalikan kartunya
                return self.__cards.pop(i)
                
        return None # Jika tidak ada satu pun kartu yang cocok di seluruh deck
    
    def return_card(self, card):
        """
        Mengembalikan satu kartu ke dalam deck dan mengocoknya.
        Digunakan untuk mendaur ulang Main Card lama.
        """
        self.__cards.append(card)
        self.shuffle()
    
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