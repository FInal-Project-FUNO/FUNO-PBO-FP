import pygame
from .base import BaseScreen
from ..core.game_manager import GameManager
from ..utils.constants import *
from ..ui.deck_animation import load_deck

class GameScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        # 1. Inisialisasi Game Manager
        from ..utils import constants
        difficulty = constants.CURRENT_DIFFICULTY
        print(f"[GAME] Starting with difficulty: {difficulty}")
        self.game = GameManager(difficulty=difficulty)
        
        # 2. Inisialisasi Font
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
        
        # 3. Load Assets (Pindahan dari main.py)
        self.loaded_cards = {}
        self._load_assets()
        
        # Variabel state
        self.selected_card_index = None
        
        # --- STATE ANIMASI ---
        self.is_choosing_color = False
        self.pending_wild_card = None # Menyimpan kartu Wild yang baru diklik
        
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        size = 100
        gap = 20
        self.color_buttons = {
            'red':   pygame.Rect(cx - size - gap, cy - size - gap, size, size),
            'green': pygame.Rect(cx + gap,        cy - size - gap, size, size),
            'blue':  pygame.Rect(cx - size - gap, cy + gap,        size, size),
            'yell':  pygame.Rect(cx + gap,        cy + gap,        size, size)
        }
        
        self.animation_state = "IDLE"  # Pilihan: IDLE, SHOW_MATCH, CLEAR
        self.animation_start_time = 0
        self.input_locked = False      # Kunci input saat animasi jalan
        
        # Snapshot Visual (Untuk menyimpan gambar kartu lama)
        self.vis_main_card = None      # Kartu Main SEBELUM berubah
        self.vis_played_card = None    # Kartu yang BARU dimainkan
        
        # Variabel pembanding untuk deteksi perubahan
        self.last_seen_played_card = None 
        # Kita simpan main card frame sebelumnya untuk snapshot
        self.prev_main_card_snapshot = self.game.main_card
        
        self.last_deck_count = self.game.deck.cards_remaining()
        
        self.final_score_timer = 0

    def _load_assets(self):
        """Memuat semua gambar kartu"""
        self.sounds = {}
        try:
            # Init mixer jika belum (biasanya sudah di main.py, tapi untuk jaga-jaga)
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            self.sounds['play'] = pygame.mixer.Sound(SOUND_PLAY_CARD)
            self.sounds['click'] = pygame.mixer.Sound(SOUND_BUTTON_CLICK)
            self.sounds['draw'] = pygame.mixer.Sound(SOUND_DRAW_CARD)
            
            # Atur volume (Opsional)
            self.sounds['play'].set_volume(0.5)
            self.sounds['click'].set_volume(0.7)
            
        except Exception as e:
            print(f"[WARNING] Gagal memuat suara: {e}")
        
        for name, path in CARD_IMAGES.items():
            try:
                game_img = pygame.image.load(BACKGROUND_PATH).convert()
                img = pygame.image.load(path)
                slot_img = pygame.image.load(SLOT_PATH).convert_alpha()
                self.loaded_cards[name] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                self.slot_image = pygame.transform.scale(slot_img, (CARD_WIDTH, CARD_HEIGHT))
                self.background_image = pygame.transform.scale(game_img, (SCREEN_WIDTH, SCREEN_HEIGHT))     

            except FileNotFoundError:
                print(f"[WARNING] File tidak ditemukan: {path}")

    def draw_card_image(self, surface, card, x, y, selected=False):
        """Fungsi helper menggambar kartu"""
        color = str(card.color).lower().strip()
        value = str(card.value).lower().strip()
        key_variants = [
            f"{color}_{value}",
            f"{color}{value}",
            f"{color}-{value}",
            f"{color} {value}"
        ]

        if value in ['wild', 'p4']:
            if value == 'wild':
                key_variants.append("wild_wild") # Paksa cari key 'wild_wild'
            elif value == 'p4':
                key_variants.append("p4_p4")
        
        image = None
        for key in key_variants:
            if key in self.loaded_cards:
                image = self.loaded_cards[key]
                break
        
        if image is None:
            image = self.loaded_cards.get("back")

        if image:
            rect = image.get_rect(topleft=(x, y))
            
            if selected:
                pygame.draw.rect(surface, COLOR_YELLOW, rect.inflate(4, 4), 3)
            
            surface.blit(image, rect)

    def _draw_shimmer(self, surface, x, y, w, h):
        """
        Membuat efek kilau cahaya (shimmer) bergerak pada kartu.
        """
        # 1. Setup Dimensi
        width = w
        height = h
        
        # 2. Hitung posisi animasi berdasarkan waktu
        # Animasi berulang setiap 1000ms (1 detik)
        period = 1000 
        current_time = pygame.time.get_ticks()
        progress = (current_time % period) / period # Nilai 0.0 s/d 1.0
        
        # 3. Buat Surface Transparan khusus untuk Shimmer
        shimmer_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 4. Gambar Pita Cahaya
        # Pita bergerak dari kiri (-width) ke kanan (+width)
        band_width = 40 
        start_x = -band_width + (width + band_width * 2) * progress
        shimmer_color = (255, 255, 255, 120) 
        
        points = [
            (start_x, 0),                 
            (start_x + band_width, 0),    
            (start_x + band_width - 20, height), 
            (start_x - 20, height)        
        ]
        
        pygame.draw.polygon(shimmer_surf, shimmer_color, points)
        
        # 5. Blit (Tempel) ke kartu
        surface.blit(shimmer_surf, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
        
    def handle_events(self, event):
        if self.input_locked:
            return
        
        # JIKA SEDANG MEMILIH WARNA (Overlay Mode)
        if self.is_choosing_color:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # Cek warna apa yang diklik
                available_colors = self._get_player_hand_colors()
                
                for color_name, rect in self.color_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        # Validasi: Hanya boleh pilih warna yang ada di tangan
                        if color_name in available_colors:
                            # EKSEKUSI FINAL: Mainkan kartu dengan warna pilihan
                            if 'click' in self.sounds:
                                self.sounds['click'].play()
                            try:
                                self.game.resolve_wild_color(color_name)
                                self.selected_card_index = None
                            except Exception as e:
                                print(f"Error: {e}")
                            
                            # Reset State
                            self.is_choosing_color = False
                            self.pending_wild_card = None
                            return
            return # Jangan lanjut ke logika game biasa        
        
        # Deteksi Klik Mouse
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game.game_over:
            mouse_x, mouse_y = event.pos
            
            # Cek kartu pemain
            player_cards = self.game.player.hand
            num_cards = len(player_cards)
        
            if num_cards > 0:
                card_spacing = 100
                start_x = (SCREEN_WIDTH -750)
                for i, card in enumerate(player_cards):
                    card_x = start_x + (i * card_spacing)
                    card_y = SCREEN_HEIGHT - CARD_HEIGHT - 25
                    # Deteksi area klik
                    if (card_x <= mouse_x <= card_x + CARD_WIDTH and
                        card_y <= mouse_y <= card_y + CARD_HEIGHT):
                        try:
                            # Panggil play_card via self.game
                            self.game.play_card(self.game.player, card)
                            self.selected_card_index = None
                        except Exception as e:
                            pass
                        break

        # Deteksi Tombol Escape untuk keluar/restart saat game over
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.game.game_over:
                self.manager.set_screen('MENU') # Kembali ke menu

    def update(self, delta_time):
        current_time = pygame.time.get_ticks()
        
        if self.animation_state == "SHOW_MATCH":
            # Tampilkan match selama 1 detik (1000ms)
            if current_time - self.animation_start_time > 500:
                self.animation_state = "CLEAR" # Pindah ke fase kosong
                
        elif self.animation_state == "CLEAR":
            # Kosongkan meja selama 0.5 detik (500ms)
            if current_time - self.animation_start_time > 700: # 1000 + 500
                self.animation_state = "IDLE"  # Selesai, tampilkan kartu baru
                self.input_locked = False      # Buka kunci input
                
        if self.game.is_waiting_for_color and not self.is_choosing_color:
            self.is_choosing_color = True
            
        if not self.game.game_over and not self.input_locked:
            self.game.update_ai()
            
            current_last_played = self.game.last_played_card
            just_played_card = (current_last_played != self.last_seen_played_card)
            if just_played_card:
                # --- PLAY SOUND (Prioritas Utama) ---
                if 'play' in self.sounds:
                    self.sounds['play'].play()
                
                # Gunakan snapshot main card frame sebelumnya (Kartu Target Lama)
                old_main = self.prev_main_card_snapshot
                self._start_transition_animation(old_main, current_last_played)
                
                # Update pembanding
                self.last_seen_played_card = current_last_played
            
            current_deck_count = self.game.deck.cards_remaining()
            
            if current_deck_count < self.last_deck_count:
                # Mainkan suara draw
                if 'draw' in self.sounds:
                    self.sounds['draw'].play()
                    
            self.last_deck_count = current_deck_count
            
            # Simpan snapshot main card saat ini untuk frame berikutnya
            self.prev_main_card_snapshot = self.game.main_card
            
        if self.input_locked:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        if self.game.is_final_condition and not self.game.game_over:
            if current_time - self.final_score_timer > 1000:
                
                # Panggil proses selanjutnya
                has_next = self.game.process_next_final_score()
                
                # Reset timer
                self.final_score_timer = current_time
                
        if not self.game.game_over and not self.input_locked:
            # Pastikan AI tidak jalan saat Final Condition
            if not self.game.is_final_condition: 
                self.game.update_ai()
                
    def _start_transition_animation(self, old_main, played_card):
        """Memulai urutan animasi visual"""
        self.animation_state = "SHOW_MATCH"
        self.vis_main_card = old_main      # Simpan kartu main yang LAMA
        self.vis_played_card = played_card # Simpan kartu yang dimainkan
        self.animation_start_time = pygame.time.get_ticks()
        self.input_locked = True           # Kunci input agar player tidak klik sembarangan

    def draw(self, surface):    
        surface.blit(self.background_image, (0, 0)) 
          
        # 1. Draw Deck (Animasi)
        cards_left = self.game.deck.cards_remaining()
        # Posisi deck
        deck_x = SCREEN_WIDTH - 830
        deck_y = SCREEN_HEIGHT - 345
        load_deck(surface, deck_x, deck_y, cards_left)
        
        # Text jumlah deck
        deck_text = self.small_font.render(f"{cards_left}", True, COLOR_BLACK)
        surface.blit(deck_text, (deck_x + 40, deck_y + CARD_HEIGHT + 12))

        # 2. Draw Main Card
        if self.game.main_card:
            main_x = SCREEN_WIDTH // 2 - CARD_WIDTH
            main_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
            played_x = main_x + 100
            
            if self.animation_state == "SHOW_MATCH":
                if self.vis_main_card:
                    self.draw_card_image(surface, self.vis_main_card, main_x, main_y)
                if self.vis_played_card:
                    self.draw_card_image(surface, self.vis_played_card, played_x, main_y)
                    
            elif self.animation_state == "CLEAR":
                pass
            
            elif self.animation_state == "IDLE":
                if self.game.main_card:
                    self.draw_card_image(surface, self.game.main_card, main_x, main_y)
                if self.slot_image:
                    surface.blit(self.slot_image, (played_x, main_y))
                    
        # 3. Draw Player Cards
        player_cards = self.game.player.hand
        num_cards = len(player_cards)
        
        if num_cards > 0:
            card_spacing = 100
            start_x = (SCREEN_WIDTH - 750)
            mx, my = pygame.mouse.get_pos()
            
            for i, card in enumerate(player_cards):
                card_x = start_x + (i * card_spacing)
                card_y = SCREEN_HEIGHT - CARD_HEIGHT - 25
                default_y = card_y
                
                temp_rect = pygame.Rect(card_x, default_y, CARD_WIDTH, CARD_HEIGHT)
                if temp_rect.collidepoint(mx, my):
                    card_y -= 15
                
                # Logic Highlight
                is_selected = (i == self.selected_card_index)
                
                # Logic Winning Pair
                is_winning_pair = False
                if self.game.game_over and (i in self.game.final_winning_indices):
                    is_winning_pair = True
                
                # 1. Gambar Kartu Dasarnya
                self.draw_card_image(surface, card, card_x, card_y, selected=is_selected)
                
                # if is_winning_pair:
                if is_winning_pair:
                    # --- LOGIC AGAR TIDAK KEGEDEAN ---                   
                    shimmer_w = CARD_WIDTH * 0.6
                    shimmer_h = CARD_HEIGHT * 0.85
                    shimmer_x = card_x + (CARD_WIDTH - shimmer_w) / 2
                    shimmer_y = card_y + (CARD_HEIGHT - shimmer_h) / 1.65
                    
                    # Panggil fungsi dengan ukuran yang sudah dikurangi padding
                    self._draw_shimmer(surface, shimmer_x, shimmer_y, shimmer_w, shimmer_h)

        # 4. Draw AI Cards (Backside)
        ai_cards = self.game.ai.hand
        ai_cards_count = len(ai_cards)        
            
        if ai_cards_count > 0:
            card_spacing = 50
            start_x = (SCREEN_WIDTH) - 650
            for i, card in enumerate(ai_cards):
                card_x = start_x + (i * card_spacing)
                card_y = 25
                back_image = self.loaded_cards.get("back")
                
                if self.game.is_final_condition or self.game.game_over:
                    card_x = start_x + (i * card_spacing)
                    card_y = 25
                    # Jika Game Over: Tampilkan Wajah Kartu (Seperti Player)
                    self.draw_card_image(surface, card, card_x, card_y)
                else:
                    # Jika Game Jalan: Tampilkan Belakang Kartu
                    if back_image:
                        surface.blit(back_image, (card_x, card_y))
                    else:
                        pygame.draw.rect(surface, COLOR_GRAY, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))

        # 5. Draw Scores
        player_score = self.font.render(f"{self.game.player.score}", True, COLOR_RED)
        ai_score = self.font.render(f"{self.game.ai.score}", True, COLOR_RED)
        
        surface.blit(player_score, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT // 2 + 30))
        surface.blit(ai_score, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT // 2 - 55))

        # 6. Draw Message (jika ada)
        if self.game.message:
            msg_text = self.small_font.render(self.game.message, True, COLOR_WHITE)
            msg_x = SCREEN_WIDTH // 2 -200
            msg_y = SCREEN_HEIGHT // 2 +80
            
            source = self.game.message_source
            
            if source == 'ai':
                msg_y = SCREEN_HEIGHT // 2 -100 
                
            surface.blit(msg_text, (msg_x, msg_y))

# 7. Draw Game Over Overlay
        if self.game.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BLACK)
            surface.blit(overlay, (0, 0))
            
            center_x = SCREEN_WIDTH // 2
            
            # 1. Judul Pemenang
            if self.game.winner:
                winner_text = self.font.render(f"{self.game.winner.name} WINS!", True, COLOR_YELLOW)
            else:
                winner_text = self.font.render("IT'S A TIE!", True, COLOR_YELLOW)
            
            # 2. Skor Akhir (FIXED: Render dulu dari string ke surface)
            score_str = f"Final Score - You: {self.game.player.score} | AI: {self.game.ai.score}"
            final_score_surf = self.font.render(score_str, True, COLOR_WHITE)
            
            # 3. Info Tambahan (Final Condition)
            # Cek apakah game berakhir karena deck habis?
            if self.game.deck.is_empty():
                 info_str = "(Includes Final Hand Pairing Points)"
                 info_surf = self.small_font.render(info_str, True, COLOR_GRAY)
                 surface.blit(info_surf, (center_x - info_surf.get_width()//2, 390))

            # 4. Tombol Restart
            restart_text = self.small_font.render("Press ESC to Main Menu", True, COLOR_WHITE)
            
            # BLIT SEMUANYA KE LAYAR
            surface.blit(winner_text, (center_x - winner_text.get_width()//2, 250))
            surface.blit(final_score_surf, (center_x - final_score_surf.get_width()//2, 350))
            surface.blit(restart_text, (center_x - restart_text.get_width()//2, 450))
            
            
        # --- GAMBAR OVERLAY PEMILIHAN WARNA ---
        if self.is_choosing_color:
            # 1. Gelapkan layar belakang
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLOR_BLACK)
            surface.blit(overlay, (0, 0))
            
            # 2. Teks Judul
            title = self.font.render("CHOOSE NEXT COLOR", True, COLOR_WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
            surface.blit(title, title_rect)
            
            # 3. Gambar 4 Kotak Warna
            available_colors = self._get_player_hand_colors()
            
            # Mapping string ke variable warna Pygame
            color_map = {
                'red': COLOR_RED, 'green': COLOR_GREEN, 
                'blue': COLOR_BLUE, 'yell': COLOR_YELLOW
            }
            
            for color_name, rect in self.color_buttons.items():
                is_available = color_name in available_colors
                
                # Tentukan warna (Terang jika available, Gelap/Abu jika tidak)
                draw_color = color_map[color_name] if is_available else (50, 50, 50)
                
                # Gambar Kotak
                pygame.draw.rect(surface, draw_color, rect, border_radius=15)
                
                # Gambar Border (Putih jika available, Hitam jika tidak)
                border_color = COLOR_WHITE if is_available else COLOR_BLACK
                pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)
                
                # (Opsional) Tanda Silang jika tidak available
                if not is_available:
                    pygame.draw.line(surface, border_color, rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(surface, border_color, rect.bottomleft, rect.topright, 3)

        # # ... (Indikator debug dll) ...
        # state_text = self.small_font.render(f"DEBUG STATE: {self.animation_state}", True, COLOR_YELLOW)
        # surface.blit(state_text, (15, 15))
        
    def _get_player_hand_colors(self):
        colors = set()
        for card in self.game.player.hand:
            if card.color in ['red', 'green', 'blue', 'yell']:
                colors.add(card.color)
        
        # PERBAIKAN: Jika tangan kosong (setelah main Wild) atau cuma isi Wild
        # Kembalikan semua warna agar tidak soft-lock
        if not colors:
            return {'red', 'green', 'blue', 'yell'}
            
        return colors