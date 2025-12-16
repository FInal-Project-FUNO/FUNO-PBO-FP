import pygame
from src.screen.base import BaseScreen
from src.core.game_manager import GameManager
from src.utils.constants import *
from src.ui.deck_animation import load_deck

class GameScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        # 1. Inisialisasi Game Manager
        self.game = GameManager() 
        
        # 2. Inisialisasi Font
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
        
        # 3. Load Assets (Pindahan dari main.py)
        self.loaded_cards = {}
        self._load_assets()
        
        # Variabel state
        self.selected_card_index = None
        
        # --- STATE ANIMASI ---
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

    def _load_assets(self):
        """Memuat semua gambar kartu"""
        for name, path in CARD_IMAGES.items():
            try:
                img = pygame.image.load(path)
                slot_img = pygame.image.load(SLOT_PATH).convert_alpha()
                self.loaded_cards[name] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                self.slot_image = pygame.transform.scale(slot_img, (CARD_WIDTH, CARD_HEIGHT))
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

    def handle_events(self, event):
        if self.input_locked:
            return
        # Deteksi Klik Mouse
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game.game_over:
            mouse_x, mouse_y = event.pos
            
            # Cek kartu pemain
            player_cards = self.game.player.hand
            for i, card in enumerate(player_cards):
                card_x = 50 + i * (CARD_WIDTH + 10)
                card_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
                
                # Deteksi area klik
                if (card_x <= mouse_x <= card_x + CARD_WIDTH and
                    card_y <= mouse_y <= card_y + CARD_HEIGHT):
                    
                    try:
                        # Panggil play_card via self.game
                        self.game.play_card(self.game.player, card)
                        self.selected_card_index = None
                    except Exception as e: # Tangkap error invalid move
                        # Akses private attribute message secara aman atau via property jika ada
                        # Di sini kita anggap property 'message' ada di GameManager
                        pass # Pesan error bisa disimpan di self.game.message

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
                print("unlock")
        
        if not self.game.game_over and not self.input_locked:
            self.game.update_ai()
            
            current_last_played = self.game.last_played_card
            
            if current_last_played != self.last_seen_played_card:
                # Wow, ada pergerakan baru!
                
                # Gunakan snapshot main card frame sebelumnya (Kartu Target Lama)
                old_main = self.prev_main_card_snapshot
                
                # Mulai animasi
                self._start_transition_animation(old_main, current_last_played)
                
                # Update pembanding
                self.last_seen_played_card = current_last_played
            
            # Simpan snapshot main card saat ini untuk frame berikutnya
            self.prev_main_card_snapshot = self.game.main_card
            
        if self.input_locked:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
    def _start_transition_animation(self, old_main, played_card):
        """Memulai urutan animasi visual"""
        self.animation_state = "SHOW_MATCH"
        self.vis_main_card = old_main      # Simpan kartu main yang LAMA
        self.vis_played_card = played_card # Simpan kartu yang dimainkan
        self.animation_start_time = pygame.time.get_ticks()
        self.input_locked = True           # Kunci input agar player tidak klik sembarangan

    def draw(self, surface):
        surface.fill(COLOR_BG)
        
        # 1. Draw Deck (Animasi)
        cards_left = self.game.deck.cards_remaining()
        # Posisi deck
        deck_x = SCREEN_WIDTH - 820
        deck_y = SCREEN_HEIGHT - 350
        load_deck(surface, deck_x, deck_y, cards_left)
        
        # Text jumlah deck
        deck_text = self.small_font.render(f"{cards_left}", True, COLOR_WHITE)
        surface.blit(deck_text, (deck_x + 50, deck_y + CARD_HEIGHT + 10))

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
            total_hand_width = ((num_cards - 1) * card_spacing) + CARD_WIDTH
            start_x = (SCREEN_WIDTH - total_hand_width) // 2
            for i, card in enumerate(player_cards):
                card_x = start_x + (i * card_spacing)
                card_y = SCREEN_HEIGHT - CARD_HEIGHT - 25
                self.draw_card_image(surface, card, card_x, card_y, i == self.selected_card_index)

        # 4. Draw AI Cards (Backside)
        ai_cards_count = self.game.ai.hand_size()
        if ai_cards_count > 0:
            card_spacing = 50
            start_x = (SCREEN_WIDTH) - 630
            for i in range(ai_cards_count):
                card_x = start_x + (i * card_spacing)
                card_y = 25
                
                back_image = self.loaded_cards.get("back")
                if back_image:
                    surface.blit(back_image, (card_x, card_y))
                else:
                    pygame.draw.rect(surface, COLOR_GRAY, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))

        # 5. Draw Scores
        player_score = self.font.render(f"Your Score: {self.game.player.score}", True, COLOR_WHITE)
        ai_score = self.font.render(f"AI Score: {self.game.ai.score}", True, COLOR_WHITE)
        
        surface.blit(player_score, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100))
        surface.blit(ai_score, (SCREEN_WIDTH - 250, 50))

        # 6. Draw Message (jika ada)
        if self.game.message:
            msg_text = self.small_font.render(self.game.message, True, COLOR_YELLOW)
            surface.blit(msg_text, (50, SCREEN_HEIGHT // 2 - 100))

        # 7. Draw Game Over Overlay
        if self.game.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BLACK)
            surface.blit(overlay, (0, 0))
            
            if self.game.winner:
                winner_text = self.font.render(f"{self.game.winner.name} WINS!", True, COLOR_YELLOW)
            else:
                winner_text = self.font.render("IT'S A TIE!", True, COLOR_YELLOW)
            
            final_score = self.font.render(
                f"Final Score - You: {self.game.player.score} | AI: {self.game.ai.score}",
                True, COLOR_WHITE
            )
            restart_text = self.small_font.render("Press ESC to Main Menu", True, COLOR_WHITE)
            
            center_x = SCREEN_WIDTH // 2
            surface.blit(winner_text, (center_x - winner_text.get_width()//2, 250))
            surface.blit(final_score, (center_x - final_score.get_width()//2, 350))
            surface.blit(restart_text, (center_x - restart_text.get_width()//2, 450))