"""
GameManager - Composition: Manages all game components
"""

from src.utils import *
from src.core import *
from src.core.effect_manager import EffectManager

class GameManager:
    """Main game manager (Composition)"""
    
    def __init__(self):
        """Initialize game manager"""
        self.__deck = Deck()
        self.__player = Player("Player")
        self.__ai = AIPlayer("AI", "medium")
        self.__main_card = None
        self.__effect_manager = EffectManager()
        self.__game_over = False
        self.__winner = None
        self.__message = ""
        
        # Deal initial cards
        self.__deal_initial_cards()
        
        # Set initial main card
        self.__set_initial_main_card()
    
    # Getters (Encapsulation)
    @property
    def deck(self):
        """Get deck"""
        return self.__deck
    
    @property
    def player(self):
        """Get human player"""
        return self.__player
    
    @property
    def ai(self):
        """Get AI player"""
        return self.__ai
    
    @property
    def main_card(self):
        """Get current main card"""
        return self.__main_card
    
    @property
    def game_over(self):
        """Check if game is over"""
        return self.__game_over
    
    @property
    def winner(self):
        """Get winner"""
        return self.__winner
    
    @property
    def message(self):
        """Get game message"""
        return self.__message
    
    def __deal_initial_cards(self):
        """Deal initial cards to players"""
        for _ in range(INITIAL_CARDS):
            try:
                self.__player.add_card(self.__deck.draw())
                self.__ai.add_card(self.__deck.draw())
            except EmptyDeckError:
                break
    
    def __set_initial_main_card(self):
        """Set initial main card"""
        try:
            self.__main_card = self.__deck.draw()
            # Make sure it's not a wild card
            while self.__main_card.value in WILD_CARDS:
                self.__main_card = self.__deck.draw()
        except EmptyDeckError:
            self.__main_card = Card('Red', '5')  # Fallback
    
    def play_card(self, player, card):
        """
        Player plays a card
        
        Args:
            player: Player object
            card: Card to play
            
        Raises:
            InvalidMoveError: If move is invalid
        """
        # Validate move
        if not card.matches(self.__main_card):
            raise InvalidMoveError(f"{card} doesn't match {self.__main_card}")
        
        # Remove card from player's hand
        if not player.remove_card(card):
            raise InvalidCardError("Card not in player's hand")
        
        # Add points
        player.add_points(card.points)
        
        # Apply effect
        effect_name = self.__effect_manager.apply_effect(card, self, player)
        if effect_name:
            self.__message = f"{player.name} played {card} - {effect_name}!"
        else:
            self.__message = f"{player.name} played {card}"
        
        # Handle wild cards
        if card.value in WILD_CARDS:
            # For AI, choose color based on hand
            if isinstance(player, AIPlayer):
                card.set_color(self.__choose_wild_color(player))
            else:
                # For human player, default to first color in hand
                colors = [c.color for c in player.hand if c.color in CARD_COLORS]
                if colors:
                    card.set_color(max(set(colors), key=colors.count))
                else:
                    card.set_color('Red')
        
        # Update main card
        self.__update_main_card()
        
        # Check win condition
        self.__check_game_over()
    
    def __choose_wild_color(self, player):
        """AI chooses color for wild card"""
        colors = [c.color for c in player.hand if c.color in CARD_COLORS]
        if colors:
            return max(set(colors), key=colors.count)
        return random.choice(CARD_COLORS)
    
    def __update_main_card(self):
        """Update main card from deck"""
        try:
            self.__main_card = self.__deck.draw()
            # Skip wild cards
            while self.__main_card.value in WILD_CARDS:
                self.__main_card = self.__deck.draw()
        except EmptyDeckError:
            self.__check_game_over()
    
    def __check_game_over(self):
        """Check if game is over"""
        # Game over if deck is empty or a player has no cards
        if self.__deck.is_empty() or self.__player.hand_size() == 0 or self.__ai.hand_size() == 0:
            self.__game_over = True
            
            # Determine winner
            if self.__player.score > self.__ai.score:
                self.__winner = self.__player
            elif self.__ai.score > self.__player.score:
                self.__winner = self.__ai
            else:
                self.__winner = None  # Tie
    
    def get_opponent(self, player):
        """Get opponent of a player"""
        return self.__ai if player == self.__player else self.__player
    
    def update_ai(self):
        """Update AI logic"""
        if not self.__game_over:
            card = self.__ai.choose_card(self.__main_card)
            if card:
                try:
                    self.play_card(self.__ai, card)
                except (InvalidMoveError, InvalidCardError):
                    pass
    
    def reset_message(self):
        """Clear game message"""
        self.__message = ""