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
        self.__ai = AIPlayer("AI", "easy")
        self.__main_card = None
        self.__effect_manager = EffectManager()
        self.__game_over = False
        self.__winner = None
        self.__message = ""
        self.__last_played_card = None
        
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
    
    @property
    def last_played_card(self):
        """Get the last card played by player or AI"""
        return self.__last_played_card
    
    def __deal_initial_cards(self):
            """Deal initial cards to players"""
            for _ in range(INITIAL_CARDS):
                try:
                    # GUNAKAN draw() BIASA UNTUK KARTU TANGAN
                    self.__player.add_card(self.__deck.draw()) 
                    self.__ai.add_card(self.__deck.draw())
                except EmptyDeckError:
                    break
    
    def __set_initial_main_card(self):
        """Set initial main card using smart validation"""
        # Panggil helper function yang sudah kita buat
        valid_card = self.__get_valid_next_main_card()
        
        if valid_card:
            self.__main_card = valid_card
        else:
            self.__main_card = Card('Red', '5') # Fallback
    
    def play_card(self, player, card):
        """
        Player plays a card
        """
        # 1. Validasi
        if not card.matches(self.__main_card):
            raise InvalidMoveError(f"{card} doesn't match {self.__main_card}")
        
        # 2. Hapus kartu dari tangan (Kartu ini menjadi poin dan TIDAK kembali ke deck)
        if not player.remove_card(card):
            raise InvalidCardError("Card not in player's hand")
        
        # point system
        points_earned = self.__calculate_dynamic_points(card, self.__main_card)
        player.add_points(points_earned)
        
        # Simpan Main Card yang sedang aktif sebelum diganti
        old_main_card = self.__main_card
        
        try:
            # 3. Masukkan Main Card lama kembali ke deck (Recycle)
            self.__deck.return_card(old_main_card)
            
            # 4. Pemain mengambil 1 kartu baru dari deck (Refill Hand)
            # Karena ini "Cepat-cepatan", tangan harus selalu diisi ulang selama deck ada
            new_card = self.__deck.draw()
            player.add_card(new_card)
            
            # 5. Update Main Card baru (Cari yang valid)
            self.__update_main_card()
            
            # Set pesan sukses
            effect_name = self.__effect_manager.apply_effect(card, self, player)
            if effect_name:
                self.__message = f"{player.name} played {card} (+{points_earned} pts) - {effect_name}!"
            else:
                self.__message = f"{player.name} played {card} (+{points_earned} pts)"

        except EmptyDeckError:
            # Jika deck habis saat proses draw/update, game selesai
            self.__check_game_over()
    
    def __choose_wild_color(self, player):
        """AI chooses color for wild card"""
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
                
    def __is_playable_by_anyone(self, target_card):
        # (Sama seperti sebelumnya: Cek apakah Player ATAU AI punya kartu yang cocok)
        player_can_play = any(c.matches(target_card) for c in self.__player.hand)
        ai_can_play = any(c.matches(target_card) for c in self.__ai.hand)
        return player_can_play or ai_can_play

    def __get_valid_next_main_card(self):
        """Minta Deck mencarikan kartu yang valid untuk dimainkan"""
        
        # 1. Definisikan syarat kartu yang kita mau
        def condition(card):
            # Syarat A: Tidak boleh Wild Card (biar warna jelas)
            if card.value in WILD_CARDS:
                return False
            # Syarat B: Harus bisa dimainkan oleh Player ATAU AI
            return self.__is_playable_by_anyone(card)
        
        # 2. Suruh deck cari kartu dengan syarat tersebut
        valid_card = self.__deck.draw_valid(condition)
        
        return valid_card    

    def __calculate_dynamic_points(self, played_card, main_card):
        """
        Menghitung poin berdasarkan aturan.
        """
        # Ambil nilai numerik dari Main Card sebagai basis pengali
        base_value = main_card.points
        
        # Cek jenis kartu yang dimainkan (Holding Card)
        val = played_card.value
        
        # Aturan d: Kartu +2 dikali 2, Kartu +4 dikali 4
        if val == 'p2': # Draw 2
            return base_value * 2
        elif val == 'p4': # Wild Draw 4
            return base_value * 4
            
        # Aturan e: Reverse, Skip, Wild bernilai sama dengan Main Card
        elif val in ['skip', 'reverse', 'wild']:
            return base_value
            
        # Aturan c: Kartu angka sesuai besaran simbolnya
        # (Termasuk jika tidak masuk kondisi di atas)
        else:
            return played_card.points
    
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