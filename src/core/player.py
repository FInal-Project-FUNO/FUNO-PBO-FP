"""
Player class - Base class for human and AI players
"""

class Player:
    """Base player class"""
    
    def __init__(self, name):
        """
        Initialize a player
        
        Args:
            name: Player name
        """
        self.__name = name
        self.__hand = []
        self.__score = 0
    
    # Getters (Encapsulation)
    @property
    def name(self):
        """Get player name"""
        return self.__name
    
    @property
    def hand(self):
        """Get player's hand (copy to prevent direct modification)"""
        return self.__hand.copy()
    
    @property
    def score(self):
        """Get player score"""
        return self.__score
    
    def add_card(self, card):
        """Add a card to player's hand"""
        self.__hand.append(card)
    
    def remove_card(self, card):
        """Remove a card from player's hand"""
        if card in self.__hand:
            self.__hand.remove(card)
            return True
        return False
    
    def add_points(self, points):
        """Add points to player's score"""
        self.__score += points
    
    def hand_size(self):
        """Get number of cards in hand"""
        return len(self.__hand)
    
    def has_valid_move(self, main_card):
        """Check if player has any valid card to play"""
        for card in self.__hand:
            if card.matches(main_card):
                return True
        return False
    
    def get_valid_cards(self, main_card):
        """Get all valid cards that can be played"""
        return [card for card in self.__hand if card.matches(main_card)]
    
    def __str__(self):
        """String representation"""
        return f"{self.__name} - Score: {self.__score}, Cards: {self.hand_size()}"