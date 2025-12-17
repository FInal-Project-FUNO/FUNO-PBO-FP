from src.utils import *
"""
Effect Manager - Polymorphism: Different effects for different card types
"""

class CardEffect:
    """Base class for card effects (Polymorphism)"""
    
    def apply_effect(self, game_manager, player):
        """
        Apply card effect
        
        Args:
            game_manager: GameManager instance
            player: Player who played the card
        """
        pass
    
    def get_effect_name(self):
        """Get effect name"""
        return "No Effect"


class SkipEffect(CardEffect):
    """Skip card effect"""
    
    def apply_effect(self, game_manager, player):
        """Skip next player's turn (not used in real-time game)"""
        game_manager.execute_skip_effect(player)
    
    def get_effect_name(self):
        return "Skip"


class ReverseEffect(CardEffect):
    """Reverse card effect"""
    
    def apply_effect(self, game_manager, player):
        """Reverse play direction (not used in 2-player game)"""
        game_manager.execute_reverse_swap(player)    
        
    def get_effect_name(self):
        return "Reverse"


class DrawTwoEffect(CardEffect):
    """Draw Two card effect"""
    
    def apply_effect(self, game_manager, player):
        pass
    
    def get_effect_name(self):
        return "point x2"


class WildDrawFourEffect(CardEffect):
    """Wild Draw Four card effect"""
    
    def apply_effect(self, game_manager, player):
        """Force opponent to draw 4 cards"""
        pass
    
    def get_effect_name(self):
        return "point x4"


class EffectManager:
    """Manages card effects (Composition)"""
    
    def __init__(self):
        """Initialize effect manager"""
        self.__effects = {
            'Skip': SkipEffect(),
            'Reverse': ReverseEffect(),
            'skip': SkipEffect(),
            'reverse': ReverseEffect(),
            'p2': DrawTwoEffect(),
            'p4': WildDrawFourEffect(),
            
        }
    
    def apply_effect(self, card, game_manager, player):
        """
        Apply effect for a card
        
        Args:
            card: Card that was played
            game_manager: GameManager instance
            player: Player who played the card
        """
        if card.value in self.__effects:
            effect = self.__effects[card.value]
            effect.apply_effect(game_manager, player)
            return effect.get_effect_name()
        return None