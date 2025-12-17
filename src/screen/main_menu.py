import pygame
import sys
from .base import BaseScreen
from ..utils.constants import *
from ..ui.components import Button 

class MainMenu(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        
        # 1. Load Background Image
        try:
            self.menu_image = pygame.image.load(MENU_PATH).convert()
            self.menu_image = pygame.transform.scale(self.menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.menu_image = None

        # 2. Setup Font untuk Overlay
        self.font_overlay = pygame.font.Font(FONT_PATH, 40) 

        # 3. Setup Tombol Utama (Invisible Hitbox)
        center_x = SCREEN_WIDTH // 2
        start_y = 250
        btn_width = 200
        btn_height = 50
        gap = 70

        self.main_buttons = [
            Button(center_x - btn_width//2, start_y, btn_width, btn_height, 
                   action=self.action_play),
            Button(center_x - btn_width//2, start_y + gap, btn_width, btn_height, 
                   action=self.action_open_difficulty), # Ganti action
            Button(center_x - btn_width//2, start_y + gap*2, btn_width, btn_height, 
                   action=self.action_exit)
        ]

        # --- SETUP OVERLAY DIFFICULTY ---
        self.show_difficulty = False
        
        # Setup Tombol Overlay (Easy, Medium, Hard)
        # Kita buat agak di tengah layar
        ov_y = SCREEN_HEIGHT // 2 - 50
        self.diff_buttons = [
            Button(center_x - 100, ov_y, 200, 50, action=lambda: self.set_difficulty('easy')),
            Button(center_x - 100, ov_y + 60, 200, 50, action=lambda: self.set_difficulty('medium')),
            Button(center_x - 100, ov_y + 120, 200, 50, action=lambda: self.set_difficulty('hard')),
        ]
        
        # Tombol Close (Klik di luar area atau tombol khusus)
        # Disini kita pakai logika: klik dimanapun selain tombol difficulty = close (di handle event)

    # --- Actions ---
    def action_play(self):
        self.manager.set_screen('GAME')

    def action_open_difficulty(self):
        self.show_difficulty = True # Buka Overlay

    def action_exit(self):
        pygame.quit()
        sys.exit()

    def set_difficulty(self, level):
        print(f"Difficulty set to: {level}")
        # Simpan settingan di ScreenManager (Variable Global Sementara)
        self.manager.selected_difficulty = level 
        self.show_difficulty = False # Tutup Overlay

    # --- Override Methods ---
    def handle_events(self, event):
        # A. JIKA OVERLAY AKTIF
        if self.show_difficulty:
            # Cek tombol difficulty
            for btn in self.diff_buttons:
                btn.handle_event(event)
            
            # Logika Tutup Overlay (Klik kanan atau Escape)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_difficulty = False
            
            return # Jangan proses tombol menu utama

        # B. JIKA MENU UTAMA BIASA
        for btn in self.main_buttons:
            btn.handle_event(event)

    def draw(self, surface):
        # 1. Gambar Background Utama
        if self.menu_image:
            surface.blit(self.menu_image, (0, 0))
        else:
            surface.fill(COLOR_BG)

        # 2. Gambar Tombol Utama (Debug Only)
        # for btn in self.main_buttons: btn.draw(surface, debug=False)

        # 3. --- GAMBAR OVERLAY ---
        if self.show_difficulty:
            # A. Layer Gelap (Dimming)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200) # Transparansi (0-255)
            overlay.fill((0, 0, 0)) # Hitam
            surface.blit(overlay, (0, 0))

            # B. Panel Judul
            title = self.font_overlay.render("SELECT DIFFICULTY", True, COLOR_WHITE)
            surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))

            # C. Gambar Tombol Difficulty (Manual Visual)
            labels = ["EASY", "MEDIUM", "HARD"]
            colors = [COLOR_GREEN, COLOR_YELLOW, COLOR_RED]
            
            for i, btn in enumerate(self.diff_buttons):
                # Gambar Kotak
                pygame.draw.rect(surface, colors[i], btn.rect, border_radius=10)
                # Gambar Border Hover
                if btn.is_hovered:
                    pygame.draw.rect(surface, COLOR_WHITE, btn.rect, 3, border_radius=10)
                
                # Gambar Teks
                text = self.font_overlay.render(labels[i], True, COLOR_BLACK)
                text_rect = text.get_rect(center=btn.rect.center)
                surface.blit(text, text_rect)