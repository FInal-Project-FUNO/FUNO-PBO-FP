"""
GameManager - Composition: Manages all game components
"""

from src.utils import *
from src.core import *
from src.core.effect_manager import EffectManager

class GameManager:
    """Main game manager (Composition)"""
    
    def __init__(self, difficulty='easy'):
        """Initialize game manager"""
        self.__deck = Deck()
        self.__player = Player("Player")
        self.__ai = AIPlayer("AI", difficulty)
        self.__main_card = None
        
        self.__effect_manager = EffectManager()
        self.__game_over = False
        self.__winner = None
        
        self.__message = ""
        self.__message_source = None 
        
        self.__last_played_card = None
        self.__waiting_for_color = False
        
        # List untuk menyimpan index kartu yang pair (untuk visual shimmer)
        self.final_winning_indices = []
        
        self.__is_final_condition = False
        self.__final_score_queue = []
        
        # FIX: Inisialisasi variabel ini SEBELUM deal cards agar tidak error
        self.__skipped_player = None
        
        self.__skipped_player = None

        # Deal initial cards
        self.__deal_initial_cards()
        # Set initial main card
        self.__set_initial_main_card()
        
    
    # Getters (Encapsulation)
    @property
    def deck(self):
        return self.__deck
    
    @property
    def player(self):
        return self.__player
    
    @property
    def ai(self):
        return self.__ai
    
    @property
    def main_card(self):
        return self.__main_card
    
    @property
    def game_over(self):
        return self.__game_over
    
    @property
    def winner(self):
        return self.__winner
    
    @property
    def message(self):
        return self.__message
    
    @property
    def message_source(self):
        return self.__message_source
    
    @property
    def last_played_card(self):
        return self.__last_played_card
    
    @property
    def is_waiting_for_color(self):
        return self.__waiting_for_color
    
    @property
    def is_final_condition(self):
        return self.__is_final_condition
    
    def __deal_initial_cards(self):
            """Deal initial cards to players"""
            for _ in range(INITIAL_CARDS):
                try:
                    self.__player.add_card(self.__deck.draw()) 
                    self.__ai.add_card(self.__deck.draw())
                except EmptyDeckError:
                    break
    
    def __set_initial_main_card(self):
        """Set initial main card using smart validation"""
        valid_card = self.__get_valid_next_main_card()
        
        if valid_card:
            self.__main_card = valid_card
        else:
            self.__main_card = Card('Red', '5') # Fallback
    
    def play_card(self, player, card, chosen_color=None):
        """Player plays a card"""
        if player.is_frozen():
            return
        
        # Cek jika player sedang di skip (Logic tambahan untuk keamanan)
        if self.__skipped_player == player:
             return

        # 1. Validasi
        if not card.matches(self.__main_card):
            raise InvalidMoveError(f"{card} doesn't match {self.__main_card}")
        
        # 2. Hapus kartu
        if not player.remove_card(card):
            raise InvalidCardError("Card not in player's hand")
        
        self.__last_played_card = card
        
        # point system
        points_earned = self.__calculate_dynamic_points(card, self.__main_card)
        player.add_points(points_earned)
        
        # Pause jika kartu Wild Card
        if card.value in WILD_CARDS and chosen_color is None and player == self.__player:
            self.__waiting_for_color = True
            self.__message = "Choose a color..."
            self.__message_source = 'player'
            return
        
        self._finalize_turn(player, card, chosen_color, points_earned)

    def resolve_wild_color(self, color):
        """Lanjutan dari play_card setelah Player memilih warna."""
        if not self.__waiting_for_color:
            return

        self.__waiting_for_color = False
        card = self.__last_played_card 
        points = self.__calculate_dynamic_points(card, self.__main_card) 
        
        self._finalize_turn(self.__player, card, color, points)

    def _finalize_turn(self, player, card, chosen_color, points_earned):
        '''internal method untuk update state setelah kartu dimainkan'''
        old_main_card = self.__main_card
        
        # Reset skipped player jika turn berhasil jalan
        if self.__skipped_player:
            self.__skipped_player = None
            
        # Apply Effect
        effect_name = self.__effect_manager.apply_effect(card, self, player)
        
        try:
            self.__deck.return_card(old_main_card)
            new_card = self.__deck.draw()
            player.add_card(new_card)
            
            # Cari main card baru (mempertimbangkan status skip)
            if chosen_color:
                self.__update_main_card_specific(chosen_color)
            else:
                self.__update_main_card()
            
            # set source 
            self.__message_source = 'player' if player == self.__player else 'ai'
                
            # Set Message Text
            base_msg = f"{player.name} +{points_earned}"
            if chosen_color:
                self.__message = f"{base_msg} ({chosen_color})!"
            elif effect_name:
                self.__message = f"{base_msg} - {effect_name}!"
            else:
                self.__message = base_msg

        except EmptyDeckError:
            self.__check_game_over()
            
    def execute_reverse_swap(self, active_player):
        """Menukar 1 kartu acak antara player dan opponent"""
        opponent = self.get_opponent(active_player)
        
        if active_player.hand_size() > 0 and opponent.hand_size() > 0:
            p_hand = active_player.hand
            o_hand = opponent.hand
            
            card_from_player = random.choice(p_hand)
            card_from_opponent = random.choice(o_hand)
            
            active_player.remove_card(card_from_player)
            opponent.remove_card(card_from_opponent)
            
            active_player.add_card(card_from_opponent)
            opponent.add_card(card_from_player)
            print(f"[EFFECT] Swapped cards")

    def execute_skip_effect(self, active_player):
        """Set status skip ke opponent"""
        self.__skipped_player = self.get_opponent(active_player)
    
    def __update_main_card_specific(self, target_color):
        def condition(card):
            return (card.color.lower() == target_color.lower()) and (card.value not in WILD_CARDS)
        
        valid_card = self.__deck.draw_valid(condition)
        if valid_card:
            self.__main_card = valid_card
        else:
            print(f"[GAME] Warna {target_color} habis! Mengambil kartu acak.")
            self.__update_main_card()
    
    def __choose_wild_color(self, player):
        colors = [c.color for c in player.hand if c.color in CARD_COLORS]
        if colors:
            return max(set(colors), key=colors.count)
        return random.choice(CARD_COLORS)
    
    def __update_main_card(self):
        valid_card = self.__get_valid_next_main_card()
        if valid_card:
            self.__main_card = valid_card
        else:
            self.__check_game_over()
            
    def __check_game_over(self):
        """Check if game is over"""
        deck_empty = self.__deck.is_empty()
        player_empty = self.__player.hand_size() == 0
        ai_empty = self.__ai.hand_size() == 0
        
        # Skenario 1: Deck Habis -> Masuk Mode Animasi Final Condition
        if deck_empty:
            if not self.__is_final_condition and not self.__game_over:
                print("\n=== DECK EMPTY! ENTERING FINAL CONDITION ===")
                self.__is_final_condition = True
                self.final_winning_indices = [] # Reset index visual
                self.__prepare_final_scores()
                # Jangan set game_over = True disini, biarkan antrian habis dulu
            
        # Skenario 2: Salah satu pemain habis kartunya -> Game Over Normal
        elif player_empty or ai_empty:
             self.__finalize_game_over()
                
    def __prepare_final_scores(self):
        """
        Menghitung pair dan memasukkannya ke antrian animasi.
        Juga menyimpan index kartu agar bisa di-highlight (shimmer) satu per satu.
        """
        
        def calculate_and_queue(hand, source_name):
            # Kita gunakan array 'used' untuk menandai kartu yang sudah dipasangkan
            # agar index tidak bergeser (tidak pakai pop)
            n = len(hand)
            used = [False] * n
            
            # 1. Pair Simbol (Prioritas)
            for i in range(n):
                if used[i]: continue
                for j in range(i + 1, n):
                    if used[j]: continue
                    
                    if hand[i].value == hand[j].value:
                        points = hand[i].points 
                        # Masukkan event ke queue beserta index-nya
                        self.__final_score_queue.append({
                            'source': source_name,
                            'points': points,
                            'indices': [i, j] if source_name == 'player' else [], # Simpan index buat player aja
                            'type': 'Symbol Pair'
                        })
                        used[i] = True
                        used[j] = True
                        break # Pindah ke kartu i berikutnya

            # 2. Pair Warna
            for i in range(n):
                if used[i]: continue
                for j in range(i + 1, n):
                    if used[j]: continue
                    
                    if hand[i].color == hand[j].color and hand[i].color not in ['wild', None]:
                        diff = abs(hand[i].points - hand[j].points)
                        if diff > 0:
                            self.__final_score_queue.append({
                                'source': source_name,
                                'points': diff,
                                'indices': [i, j] if source_name == 'player' else [],
                                'type': 'Color Pair'
                            })
                        used[i] = True
                        used[j] = True
                        break

        # Masukkan event Player dulu, baru AI
        calculate_and_queue(self.__player.hand, 'player')
        calculate_and_queue(self.__ai.hand, 'ai')

    def process_next_final_score(self):
        """
        Dipanggil oleh GameScreen setiap detik.
        Mengambil satu event dari antrian, update skor, dan update visual shimmer.
        """
        # Jika antrian habis, baru finalisasi game over
        if not self.__final_score_queue:
            self.__finalize_game_over()
            return False 

        event = self.__final_score_queue.pop(0)
        source = event['source']
        points = event['points']
        indices = event.get('indices', [])
        pair_type = event.get('type', 'Pair')
        
        # --- LOGGING KE TERMINAL ---
        print(f"[FINAL SCORE] {source.title()} gets +{points} pts ({pair_type})")
        # ---------------------------
        
        if source == 'player':
            self.__player.add_points(points)
            self.__message_source = 'player'
            # Update visual shimmer secara bertahap!
            self.final_winning_indices.extend(indices)
        else:
            self.__ai.add_points(points)
            self.__message_source = 'ai'
            
        self.__message = f"+{points}" # Tampilkan "+4" dsb
        return True

    def __finalize_game_over(self):
        """Finalisasi Game Over dan Tentukan Pemenang"""
        print("=== GAME OVER ===")
        self.__game_over = True
        self.__is_final_condition = False
        self.__message = "" 
        
        if self.__player.score > self.__ai.score:
            self.__winner = self.__player
        elif self.__ai.score > self.__player.score:
            self.__winner = self.__ai
        else:
            self.__winner = None
                
    def __is_playable_by_anyone(self, target_card):
        player_can_play = any(c.matches(target_card) for c in self.__player.hand)
        ai_can_play = any(c.matches(target_card) for c in self.__ai.hand)
        return player_can_play or ai_can_play

    def __get_valid_next_main_card(self):
        """Minta Deck mencarikan kartu yang valid untuk dimainkan"""
        def condition(card):
            if card.value in WILD_CARDS: return False
            
            # Jika ada status skip, pastikan kartu cocok untuk Active Player
            if self.__skipped_player:
                active_player = self.get_opponent(self.__skipped_player)
                return any(c.matches(card) for c in active_player.hand)
            
            return self.__is_playable_by_anyone(card)
        
        return self.__deck.draw_valid(condition)    

    def __calculate_dynamic_points(self, played_card, main_card):
        base_value = main_card.points
        val = played_card.value

        if main_card.is_special():
            return played_card.points
        
        if val == 'p2': return base_value * 2
        elif val == 'p4': return base_value * 4
        elif val in ['skip', 'reverse', 'wild']: return base_value
        else: return played_card.points
        
    def __calculate_final_score(self, hand):
        # Method ini sudah digantikan oleh logic di __prepare_final_scores
        # Bisa dihapus atau dibiarkan kosong
        pass
    
    def get_opponent(self, player):
        return self.__ai if player == self.__player else self.__player
    
    def update_ai(self):
        if self.__game_over or self.__waiting_for_color:
            return
        if self.__skipped_player == self.__ai:
            return
        
        card = self.__ai.choose_card(self.__main_card)
        if card:
            try:
                self.play_card(self.__ai, card)
            except (InvalidMoveError, InvalidCardError):
                pass
    
    def reset_message(self):
        self.__message = ""