"""
AIPlayer class - Inheritance: extends Player with AI logic
"""
import time
import random
from src.utils import *
from src.core import *
from src.core.player import Player

class AIPlayer(Player):
    """AI Player - inherits from Player"""
    
    def __init__(self, name="AI", difficulty="medium"):
        """
        Initialize AI player
        
        Args:
            name: AI name
            difficulty: AI difficulty level (easy, medium, hard)
        """
        super().__init__(name)
        self.__difficulty = difficulty
        self.__last_move_time = 0
    
    def choose_card(self, main_card):
        """
        AI chooses a card to play (Polymorphism - can be overridden)
        
        Args:
            main_card: Current main card
            
        Returns:
            Card or None: Card to play or None if no valid card
        """
        # Add delay to make AI feel more natural
        current_time = time.time()
        if current_time - self.__last_move_time < AI_DELAY:
            return None
        
        valid_cards = self.get_valid_cards(main_card)
        
        if not valid_cards:
            return None
        
        # AI strategy based on difficulty
        if self.__difficulty == "easy":
            chosen = valid_cards[0]  # Play first valid card
        elif self.__difficulty == "hard":
            # Play highest point card
            chosen = max(valid_cards, key=lambda c: c.points)
        else:  # medium
            # Play special cards first, then random
            special_cards = [c for c in valid_cards if c.is_special()]
            chosen = special_cards[0] if special_cards else random.choice(valid_cards)
        
        self.__last_move_time = current_time
        return chosen