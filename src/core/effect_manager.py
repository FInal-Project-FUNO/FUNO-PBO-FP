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
    def apply_effect(self, game_manager, player):
        # KONSEP FUNO: Freeze Lawan
        opponent = game_manager.get_opponent(player)
        # Kita butuh method 'freeze' di class Player (Lihat poin B)
        if hasattr(opponent, 'freeze'):
            opponent.freeze(2)
            
    def get_effect_name(self):
        return "SKIP! (Enemy Frozen)"


class ReverseEffect(CardEffect):
    def apply_effect(self, game_manager, player):
        # KONSEP FUNO: Tukar 1 Kartu Acak
        opponent = game_manager.get_opponent(player)
        
        # Cek validitas tangan
        if player.hand_size() > 0 and opponent.hand_size() > 0:
            # Ambil index acak
            my_idx = random.randint(0, player.hand_size() - 1)
            opp_idx = random.randint(0, opponent.hand_size() - 1)
            
            # Ambil object kartu
            my_card = player.hand[my_idx]
            opp_card = opponent.hand[opp_idx]
            
            # Lakukan pertukaran
            player.remove_card(my_card)
            opponent.remove_card(opp_card)
            
            player.add_card(opp_card)
            opponent.add_card(my_card)

    def get_effect_name(self):
        return "REVERSE! (Card Swapped)"


class DrawTwoEffect(CardEffect):
    def apply_effect(self, game_manager, player):
        pass 
    def get_effect_name(self):
        return "SCORE x2!"

class WildDrawFourEffect(CardEffect):
    def apply_effect(self, game_manager, player):
        pass
    def get_effect_name(self):
        return "SCORE x4!"


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