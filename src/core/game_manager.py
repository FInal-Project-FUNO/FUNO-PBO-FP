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
        
        self.__is_final_condition = False
        self.__final_score_queue = []
        
        # Deal initial cards
        self.__deal_initial_cards()
        # Set initial main card
        self.__set_initial_main_card()
        
        self.__skipped_player = None
    
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
    def message_source(self):
        return self.__message_source
    
    @property
    def last_played_card(self):
        """Get the last card played by player or AI"""
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
    
    def play_card(self, player, card, chosen_color=None):
        """
        Player plays a card
        args : choose color for wild card
        """
        # Jika Player sedang di-skip, tolak langkah (opsional, harusnya dihandle UI juga)
        if self.__skipped_player == player:
            # raise InvalidMoveError("You are skipped!") 
            # Atau return saja
            return        
        
        # 1. Validasi
        if not card.matches(self.__main_card):
            raise InvalidMoveError(f"{card} doesn't match {self.__main_card}")
        
        # 2. Hapus kartu dari tangan (Kartu ini menjadi poin dan TIDAK kembali ke deck)
        if not player.remove_card(card):
            raise InvalidCardError("Card not in player's hand")
        
        self.__last_played_card = card
        
        # point system
        points_earned = self.__calculate_dynamic_points(card, self.__main_card)
        player.add_points(points_earned)
        
        #Pause jika kartu Wild Card
        if card.value in WILD_CARDS and chosen_color is None and player == self.__player:
            self.__waiting_for_color = True
            self.__message = "Choose a color..."
            self.__message_source = 'player'
            return
        
        self._finalize_turn(player, card, chosen_color, points_earned)

    def resolve_wild_color(self, color):
        """
        Lanjutan dari play_card setelah Player memilih warna lewat Overlay.
        """
        if not self.__waiting_for_color:
            return

        # Matikan status waiting
        self.__waiting_for_color = False
        
        # Lanjutkan proses game yang tertunda
        # Kita ambil kartu terakhir yang dimainkan player
        card = self.__last_played_card 
        points = self.__calculate_dynamic_points(card, self.__main_card) # Recalculate or use saved
        
        self._finalize_turn(self.__player, card, color, points)

    def _finalize_turn(self, player, card, chosen_color, points_earned):
        '''internal method untuk update state setelah kartu dimainkan'''
        old_main_card = self.__main_card
        try:
            self.__deck.return_card(old_main_card)
            new_card = self.__deck.draw()
            player.add_card(new_card)
            
            self.__update_main_card()
            
            # set source 
            if player == self.__player:
                self.__message_source = 'player'
            else:
                self.__message_source = 'ai'
                
            #Update Main Card 
            if chosen_color:
                # Jika ada request warna (dari Wild Card), cari Main Card spesifik
                self.__update_main_card_specific(chosen_color)
                self.__message = f" +{points_earned} ({chosen_color}) !"
            else:
                # Normal update
                self.__update_main_card()
                self.__message = f"{player.name} +{points_earned})"
            
            #Reset skipped player setelah giliran selesai
            if self.__skipped_player:
                self.__skipped_player = None
            
            # Set effect
            effect_name = self.__effect_manager.apply_effect(card, self, player)
            if effect_name:
                self.__message = f"{player.name} +{points_earned} - {effect_name}!"
            else:
                self.__message = f"{player.name} +{points_earned}"

        except EmptyDeckError:
            # Jika deck habis saat proses draw/update, game selesai
            self.__check_game_over()
            
    def execute_reverse_swap(self, active_player):
        """Menukar 1 kartu acak antara player dan opponent"""
        opponent = self.get_opponent(active_player)
        
        # Pastikan kedua pihak punya kartu untuk ditukar
        if active_player.hand_size() > 0 and opponent.hand_size() > 0:
            # Ambil copy hand (karena property hand mengembalikan copy)
            p_hand = active_player.hand
            o_hand = opponent.hand
            
            # Pilih kartu acak
            card_from_player = random.choice(p_hand)
            card_from_opponent = random.choice(o_hand)
            
            # Lakukan pertukaran (Hapus lalu Tambah)
            active_player.remove_card(card_from_player)
            opponent.remove_card(card_from_opponent)
            
            active_player.add_card(card_from_opponent)
            opponent.add_card(card_from_player)
            
            print(f"[EFFECT] Swapped {card_from_player} with {card_from_opponent}")

    # Helper baru untuk Skip Effect
    def execute_skip_effect(self, active_player):
        """Set status skip ke opponent"""
        self.__skipped_player = self.get_opponent(active_player)
    
    def __update_main_card_specific(self, target_color):
        """Mencari kartu main baru yang warnanya SESUAI pilihan pemain"""
        
        def condition(card):
            # Syarat: Warna harus sama dengan target & Bukan Wild
            return (card.color.lower() == target_color.lower()) and (card.value not in WILD_CARDS)
        
        # Cari di deck
        valid_card = self.__deck.draw_valid(condition)
        
        if valid_card:
            self.__main_card = valid_card
        else:
            # Fallback: Jika warna yang diminta HABIS di deck, cari apa saja yang valid
            print(f"[GAME] Warna {target_color} habis! Mengambil kartu acak.")
            self.__update_main_card()
    
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
        
        deck_empty = self.__deck.is_empty()
        player_empty = self.__player.hand_size() == 0
        ai_empty = self.__ai.hand_size() == 0
        
        
        if deck_empty:
            if not self.__is_final_condition and not self.__game_over:
                self.__is_final_condition = True
                self.__prepare_final_scores()
            
            elif player_empty or ai_empty:
             # JIKA KARTU TANGAN HABIS: Game Over Normal
             self.__finalize_game_over()
            
            # --- FINAL CONDITION CALCULATION ---
            # Jika Deck habis, buka kartu sisa (Holding Cards) & hitung Pair
            if deck_empty:
                player_final_pts = self.__calculate_final_score(self.__player.hand)
                ai_final_pts = self.__calculate_final_score(self.__ai.hand)
                
                # Tambahkan ke skor total
                self.__player.add_points(player_final_pts)
                self.__ai.add_points(ai_final_pts)
                
                print(f"[FINAL] Deck Empty! Final Calculation:")
                print(f"Player Hand Points: +{player_final_pts}")
                print(f"AI Hand Points: +{ai_final_pts}")
            
            # Determine winner
            if self.__player.score > self.__ai.score:
                self.__winner = self.__player
            elif self.__ai.score > self.__player.score:
                self.__winner = self.__ai
            else:
                self.__winner = None  # Tie
                
    def __prepare_final_scores(self):
        """Menghitung pair dan memasukkannya ke antrian animasi"""
        
        # Helper untuk mencari pair di satu tangan
        def get_pair_events(hand, source_name):
            events = []
            cards = hand[:] # Copy agar tidak merusak list asli
            
            # 1. Pair Simbol
            i = 0
            while i < len(cards):
                paired = False
                for j in range(i + 1, len(cards)):
                    if cards[i].value == cards[j].value:
                        points = cards[i].points 
                        events.append({'source': source_name, 'points': points, 'desc': 'Symbol Pair'})
                        cards.pop(j); cards.pop(i)
                        paired = True; break
                if not paired: i += 1

            # 2. Pair Warna
            i = 0
            while i < len(cards):
                paired = False
                for j in range(i + 1, len(cards)):
                    if cards[i].color == cards[j].color and cards[i].color not in ['wild', None]:
                        diff = abs(cards[i].points - cards[j].points)
                        if diff > 0: # Hanya jika ada poin
                            events.append({'source': source_name, 'points': diff, 'desc': 'Color Pair'})
                        cards.pop(j); cards.pop(i)
                        paired = True; break
                if not paired: i += 1
            
            return events

        # Masukkan hasil Player dulu, baru AI
        self.__final_score_queue.extend(get_pair_events(self.__player.hand, 'player'))
        self.__final_score_queue.extend(get_pair_events(self.__ai.hand, 'ai'))

    def process_next_final_score(self):
        """
        Dipanggil oleh GameScreen setiap X detik.
        Mengambil satu event dari antrian dan menampilkannya.
        """
        # Jika antrian habis, selesai!
        if not self.__final_score_queue:
            self.__finalize_game_over()
            return False 

        # Ambil satu event
        event = self.__final_score_queue.pop(0)
        source = event['source']
        points = event['points']
        
        # Tambah Poin & Set Pesan
        if source == 'player':
            self.__player.add_points(points)
            self.__message_source = 'player'
        else:
            self.__ai.add_points(points)
            self.__message_source = 'ai'
            
        self.__message = f"+{points}" # Tampilkan "+4" dsb
        return True

    def __finalize_game_over(self):
        """Finalisasi Game Over dan Tentukan Pemenang"""
        self.__game_over = True
        self.__is_final_condition = False
        self.__message = "" # Bersihkan pesan poin terakhir
        
        if self.__player.score > self.__ai.score:
            self.__winner = self.__player
        elif self.__ai.score > self.__player.score:
            self.__winner = self.__ai
        else:
            self.__winner = None
                
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

        if main_card.is_special():
            return played_card.points
        
        # Aturan d: Kartu +2 dikali 2, Kartu +4 dikali 4
        if val == 'p2': # Draw 2
            return base_value * 2
        elif val == 'p4': # Wild Draw 4
            return base_value * 4
            
        # Aturan e: Reverse, Skip, Wild bernilai sama dengan Main Card
        elif val in ['skip', 'reverse', 'wild']:
            return base_value
            
        else:
            return played_card.points
        
    def __calculate_final_score(self, hand):
        """
        Menghitung poin Final Condition berdasarkan Pair.
        Aturan:
        1. Prioritas: Pair Simbol (Value sama). Poin = Nilai Kartu (Special=10).
        2. Sekunder: Pair Warna (Color sama). Poin = Selisih Nilai kedua kartu.
        3. Sisanya 0 poin.
        """
        # Salin list agar tidak merusak data asli saat proses pop()
        cards = hand[:] 
        final_points = 0
        
        # --- STEP 1: Cek Pair Simbol (Prioritas Utama) ---
        i = 0
        while i < len(cards):
            card_a = cards[i]
            paired = False
            
            # Cari pasangan di kartu sisa
            for j in range(i + 1, len(cards)):
                card_b = cards[j]
                
                # Cek Value Sama (Misal: 4 Merah & 4 Biru)
                if card_a.value == card_b.value:
                    # HIT: Pair Simbol
                    # Poin = Nilai Kartu itu sendiri (Sesuai aturan f)
                    # (Card points sudah diset 10 untuk special di constants.py)
                    points = card_a.points 
                    final_points += points
                    
                    # Hapus kartu yang sudah berpasangan
                    # Hapus index j (belakang) dulu biar index i gak geser
                    cards.pop(j)
                    cards.pop(i)
                    
                    paired = True
                    break # Keluar loop inner, lanjut loop outer
            
            if not paired:
                i += 1 # Lanjut cek kartu berikutnya
        
        # --- STEP 2: Cek Pair Warna (Kartu Sisa) ---
        i = 0
        while i < len(cards):
            card_a = cards[i]
            paired = False
            
            for j in range(i + 1, len(cards)):
                card_b = cards[j]
                
                # Cek Warna Sama (Misal: 8 Hijau & 3 Hijau)
                # Pastikan bukan Wild (Wild biasanya tidak punya warna kecuali dimainkan)
                if card_a.color == card_b.color and card_a.color not in ['wild', None]:
                    # HIT: Pair Warna
                    # Poin = Selisih Nilai (Absolute Difference)
                    diff = abs(card_a.points - card_b.points)
                    final_points += diff
                    
                    cards.pop(j)
                    cards.pop(i)
                    
                    paired = True
                    break
            
            if not paired:
                i += 1
                
        return final_points
    
    def get_opponent(self, player):
        """Get opponent of a player"""
        return self.__ai if player == self.__player else self.__player
    
    def update_ai(self):
        """Update AI logic"""
        if self.__game_over:
            return
        if self.__waiting_for_color:
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
        """Clear game message"""
        self.__message = ""