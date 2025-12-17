import pygame
import sys
from .base import BaseScreen
from ..utils.constants import *
from ..ui.components import Button 

class MainMenu(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        
        # 1. Load Background Image (Sekali saja di awal agar efisien)
        # Pastikan gambar MENU_PATH ini SUDAH ADA gambar tombol/teks visualnya
        try:
            self.menu_image = pygame.image.load(MENU_PATH).convert()
            # Opsional: Scale gambar agar pas layar
            self.menu_image = pygame.transform.scale(self.menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"[WARNING] Gagal memuat gambar menu: {e}")
            self.menu_image = None # Fallback

        # 2. Setup Posisi Hitbox
        # PENTING: Koordinat (x, y) ini harus Anda sesuaikan manual 
        # agar pas menimpa gambar tombol di background.
        center_x = SCREEN_WIDTH // 2
        start_y = 250
        btn_width = 200
        btn_height = 50
        gap = 80

        # 3. Inisialisasi Tombol (Invisible Hitbox)
        # Parameter: x, y, width, height, action
        self.buttons = [
            # Tombol Play
            Button(center_x - btn_width//2, start_y, btn_width, btn_height, 
                   action=self.action_play),
            
            # Tombol Difficulty
            Button(center_x - btn_width//2, start_y + gap, btn_width, btn_height, 
                   action=self.action_difficulty),
            
            # Tombol Exit
            Button(center_x - btn_width//2, start_y + gap*2, btn_width, btn_height, 
                   action=self.action_exit)
        ]

    # --- Actions / Callbacks ---
    def action_play(self):
        print("Pindah ke Game Screen")
        self.manager.set_screen('GAME')

    def action_difficulty(self):
        print("Pindah ke Difficulty Screen")
        # self.manager.set_screen('DIFFICULTY')
        pass 

    def action_exit(self):
        pygame.quit()
        sys.exit()

    # --- Override Methods ---
    def handle_events(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, delta_time):
        pass 

    def draw(self, surface):
        # 1. Gambar Background Visual (Gambar tombol ada di sini)
        if self.menu_image:
            surface.blit(self.menu_image, (0, 0))
        else:
            surface.fill(COLOR_BG) # Fallback warna solid

        # 2. Draw Hitbox 
        # Secara default ini tidak akan menggambar apa-apa (invisible).
        # Gunakan debug=True jika ingin melihat kotak merah/hijau untuk mengepaskan posisi.
        for btn in self.buttons:
            btn.draw(surface, debug=False)