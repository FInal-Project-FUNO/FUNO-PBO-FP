# """
# AIPlayer class - Inheritance: extends Player with AI logic
# """
# import time
# import random
# from src.utils import *
# from src.core import *
# from src.core.player import Player

# class AIPlayer(Player):
#     """AI Player - inherits from Player"""
    
#     def __init__(self, name="AI", difficulty="medium"):
#         """
#         Initialize AI player
        
#         Args:
#             name: AI name
#             difficulty: AI difficulty level (easy, medium, hard)
#         """
#         super().__init__(name)
#         self.__difficulty = difficulty
#         self.__last_move_time = time.time()
    
#     def choose_card(self, main_card):
#         """
#         AI chooses a card to play (Polymorphism - can be overridden)
        
#         Args:
#             main_card: Current main card
            
#         Returns:
#             Card or None: Card to play or None if no valid card
#         """
#         # Add delay to make AI feel more natural
#         current_time = time.time()
#         if current_time - self.__last_move_time < AI_DELAY:
#             return None
        
#         valid_cards = self.get_valid_cards(main_card)
        
#         if not valid_cards:
#             return None
        
#         # AI strategy based on difficulty
#         if self.__difficulty == "easy":
#             chosen = valid_cards[0]  # Play first valid card
#         elif self.__difficulty == "hard":
#             # Play highest point card
#             chosen = max(valid_cards, key=lambda c: c.points)
#         else:  # medium
#             # Play special cards first, then random
#             special_cards = [c for c in valid_cards if c.is_special()]
#             chosen = special_cards[0] if special_cards else random.choice(valid_cards)
        
#         self.__last_move_time = current_time
#         return chosen

"""
AIPlayer class - Inheritance: extends Player with AI logic
"""
import time
import random
from src.utils import *
from src.core import *
from src.core.player import Player

class AIPlayer(Player):
    """AI Player - inherits from Player with Human-like Reaction Logic"""
    
    def __init__(self, name="AI", difficulty="medium"):
        """
        Initialize AI player
        Args:
            name: AI name
            difficulty: 'easy', 'medium', 'hard'
        """
        super().__init__(name)
        self.__difficulty = difficulty.lower()
        
        # --- State Reaksi Manusia ---
        self.__last_seen_main_card = None  # Kartu terakhir yang dilihat AI di meja
        self.__reaction_end_time = 0       # Kapan AI selesai "mikir"
        self.__is_thinking = False         # Status apakah sedang memproses visual
        
        # Momentum (Untuk Adaptive Speed)
        self.__momentum_speed_boost = 0.0
    
    def choose_card(self, main_card):
        """
        AI Decision Logic (Called every frame/tick)
        Menggunakan konsep 'Reaction Time' alih-alih delay statis.
        """
        current_time = time.time()
        
        # 1. DETEKSI PERUBAHAN VISUAL (Main Card Berubah)
        # Jika kartu di meja berubah (misal Player baru saja menurunkan kartu),
        # AI harus "bereaksi ulang" (Reset timer).
        if str(main_card) != str(self.__last_seen_main_card):
            self.__last_seen_main_card = str(main_card) # Simpan snapshot baru
            self.__start_thinking_process(current_time) # Reset waktu mikir
            return None # Belum bisa jalan, baru sadar kartu ganti
            
        # 2. PROSES BERPIKIR (Waiting for Reaction Time)
        if current_time < self.__reaction_end_time:
            return None # Masih mikir/gerak mouse
            
        # 3. EKSEKUSI (Waktu mikir selesai)
        valid_cards = self.get_valid_cards(main_card)
        
        if not valid_cards:
            # Jika tidak punya kartu, AI diam saja (menunggu main card berubah lagi/draw)
            # Opsional: Reset timer biar gak spam logic checking
            self.__reaction_end_time = current_time + 0.5 
            self.__momentum_speed_boost = 0.0 # Kehilangan momentum
            return None
            
        # Pilih kartu berdasarkan strategi
        chosen_card = self.__apply_strategy(valid_cards)
        
        # Jika berhasil memilih, kita tambah momentum (khusus Hard)
        if self.__difficulty == 'hard':
            self.__momentum_speed_boost = min(0.2, self.__momentum_speed_boost + 0.05)
            
        # Reset state agar tidak spamming kartu yang sama di frame berikutnya
        # Kita set reaction time sedikit ke depan untuk simulasi "Cooldown" klik
        self.__reaction_end_time = current_time + 2.0 
        
        return chosen_card

    def __start_thinking_process(self, current_time):
        """Menghitung seberapa cepat AI bereaksi terhadap kartu baru"""
        base_delay = 0.0
        random_var = 0.0
        
        if self.__difficulty == "easy":
            # Lambat: 1.5 sampai 2.5 detik
            base_delay = 1.5
            random_var = random.uniform(0.0, 1.0)
            
        elif self.__difficulty == "medium":
            # Normal: 0.8 sampai 1.5 detik
            base_delay = 0.8
            random_var = random.uniform(0.0, 0.7)
            
        elif self.__difficulty == "hard":
            # Cepat: 0.4 sampai 0.8 detik
            base_delay = 0.4
            random_var = random.uniform(0.0, 0.4)
            
            # ADAPTIVE: Dikurangi momentum (makin sering benar, makin cepat)
            base_delay = max(0.2, base_delay - self.__momentum_speed_boost)

        total_delay = base_delay + random_var
        self.__reaction_end_time = current_time + total_delay

    def __apply_strategy(self, valid_cards):
        """Strategi pemilihan kartu"""
        
        # STRATEGI EASY: Asal pilih (Random)
        if self.__difficulty == "easy":
            return random.choice(valid_cards)
            
        # STRATEGI MEDIUM: Prioritaskan Special, lalu Warna
        elif self.__difficulty == "medium":
            specials = [c for c in valid_cards if c.is_special()]
            if specials:
                return random.choice(specials) # Suka nyerang
            return valid_cards[0] # Kalau gak ada special, pakai kartu pertama
            
        # STRATEGI HARD: Min-Maxing (Poin Tertinggi & Combo)
        elif self.__difficulty == "hard":
            # 1. Cari yang poinnya paling besar (+2, +4, Skip)
            # Logic: sorted descending by points
            valid_cards.sort(key=lambda c: c.points, reverse=True)
            
            best_card = valid_cards[0]
            
            # Tambahan Logic: Jangan buang Wild Card kalau masih ada kartu warna
            # Kecuali Wild Card adalah satu-satunya jalan
            colored_cards = [c for c in valid_cards if c.value not in ['wild', 'p4']]
            if colored_cards and best_card.value in ['wild', 'p4']:
                # Simpan Wild buat nanti, pakai kartu warna point tertinggi dulu
                return max(colored_cards, key=lambda c: c.points)
                
            return best_card
            
        return valid_cards[0]