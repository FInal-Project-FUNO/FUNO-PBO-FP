import pygame
import sys
from .base import BaseScreen
from ..utils.constants import *
from ..ui.components import Button

# --- CLASS TAMBAHAN UNTUK POPUP ---
class DifficultyPopup:
    """Helper class untuk menangani tampilan dan logika popup difficulty"""
    def __init__(self, manager, on_close_callback):
        self.manager = manager
        self.on_close = on_close_callback # Fungsi yang dipanggil saat popup ditutup
        self.font_title = pygame.font.Font(FONT_PATH, 48)
        self.font_btn = pygame.font.Font(FONT_PATH, 32)

        # --- Layout Popup ---
        self.width = 500
        self.height = 400
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # --- Layout Tombol di dalam Popup ---
        btn_w = 250
        btn_h = 60
        gap = 20
        start_y = self.y + 120
        center_x = self.x + (self.width - btn_w) // 2

        # Data Tombol: Label, Difficulty Value, Warna Dasar
        self.button_data = [
            ("BABY", "easy", (114, 203, 59)),   # Hijau
            ("KID", "medium", (255, 213, 0)), # Kuning
            ("MAN", "hard", (223, 50, 19))    # Merah 
        ]

        self.buttons = []
        for i, data in enumerate(self.button_data):
            label, diff_value, color = data
            # Kita gunakan lambda untuk mengikat nilai difficulty ke fungsi set_difficulty
            action = lambda v=diff_value: self.set_difficulty(v)
            
            btn_rect = pygame.Rect(center_x, start_y + i*(btn_h+gap), btn_w, btn_h)
            # Simpan rect, label, color, dan objek Button hitboxnya
            self.buttons.append({
                'rect': btn_rect,
                'label': label,
                'color': color,
                'hitbox': Button(btn_rect.x, btn_rect.y, btn_w, btn_h, action=action)
            })

    def set_difficulty(self, level):
        print(f"[Popup] Difficulty changed to: {level}")
        # --- SIMPAN SETTING DI SINI ---
        # Cara paling gampang: simpan di manager jika manager punya dictionary settings
        # self.manager.game_settings['difficulty'] = level
        
        # ATAU update constant global (harus import di dalam fungsi)
        from ..utils import constants
        constants.CURRENT_DIFFICULTY = level

        # Tutup popup setelah memilih
        self.on_close()

    def handle_event(self, event):
        # Cek klik pada tombol-tombol difficulty
        for btn_data in self.buttons:
            btn_data['hitbox'].handle_event(event)
            
        # Opsional: Klik di luar area popup untuk menutup
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.on_close()

    def draw(self, surface):
        # 1. Overlay Gelap (Dimmer Background)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180) # Lebih gelap dari sebelumnya
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 2. Panel Popup (Background & Border)
        # Warna panel agak abu-abu kebiruan
        panel_color = (60, 60, 80) 
        border_color = (200, 200, 200)
        
        # Gambar shadow sedikit agar menonjol
        pygame.draw.rect(surface, (30, 30, 30), self.rect.move(5, 5), border_radius=15)
        # Gambar panel utama
        pygame.draw.rect(surface, panel_color, self.rect, border_radius=15)
        # Gambar border
        pygame.draw.rect(surface, border_color, self.rect, 4, border_radius=15)

        # 3. Judul Popup
        title_surf = self.font_title.render("DIFFICULTY", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.x + self.width//2, self.y + 60))
        surface.blit(title_surf, title_rect)

        # 4. Gambar Tombol-tombol (Manual Drawing agar terlihat lebih bagus)
        mouse_pos = pygame.mouse.get_pos()
        for btn_data in self.buttons:
            rect = btn_data['rect']
            base_color = btn_data['color']
            label = btn_data['label']

            # Efek Hover Sederhana
            draw_color = base_color
            if rect.collidepoint(mouse_pos):
                # Buat warna lebih terang saat di-hover
                draw_color = [min(c + 30, 255) for c in base_color]
            
            # Gambar Rect Tombol
            pygame.draw.rect(surface, draw_color, rect, border_radius=8)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=8) # Border tombol putih tipis

            # Gambar Teks Label di tengah tombol
            text_surf = self.font_btn.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center) 
            shift_y = 5
            text_rect.y -= shift_y
            # Sedikit shadow pada teks agar terbaca jelas
            shadow_surf = self.font_btn.render(label, True, (0, 0, 0))
            surface.blit(shadow_surf, text_rect.move(2, 2))
            surface.blit(text_surf, text_rect)

            # Debug hitbox jika perlu
            # btn_data['hitbox'].draw(surface, debug=True)


# --- MAIN MENU SCREEN CLASS ---
class MainMenu(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        
        # --- Setup Background & Aset ---
        try:
            self.menu_image = pygame.image.load(MENU_PATH).convert()
            self.menu_image = pygame.transform.scale(self.menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"[WARNING] Menu image not found: {e}")
            self.menu_image = None
            self.bg_color = (40, 40, 50) # Warna fallback yang lebih bagus

        # --- Setup Tombol Menu Utama (Invisible Hitboxes) ---
        # Sesuaikan koordinat ini dengan gambar background Anda
        center_x = SCREEN_WIDTH // 2
        start_y = 250 
        btn_w, btn_h = 200, 50
        gap = 80

        self.main_buttons = [
            Button(center_x - btn_w//2, start_y, btn_w, btn_h, action=self.action_play),
            Button(center_x - btn_w//2, start_y + gap, btn_w, btn_h, action=self.action_open_difficulty),
            Button(center_x - btn_w//2, start_y + gap*2, btn_w, btn_h, action=self.action_exit)
        ]

        # --- Setup Popup System ---
        self.show_popup = False
        # Kita buat instance popup, berikan callback function 'close_popup'
        self.difficulty_popup = DifficultyPopup(self.manager, self.close_popup)

    # --- Actions Menu Utama ---
    def action_play(self):
        # Cek dulu difficulty yang terpilih (opsional, untuk debug)
        from ..utils import constants
        print(f"Starting Game with difficulty: {getattr(constants, 'CURRENT_DIFFICULTY', 'Not Set')}")
        self.manager.set_screen('GAME')

    def action_open_difficulty(self):
        self.show_popup = True # Aktifkan mode popup

    def action_exit(self):
        pygame.quit()
        sys.exit()

    # --- Callback dari Popup ---
    def close_popup(self):
        self.show_popup = False # Kembali ke mode menu utama

    # --- Core Logic ---
    def handle_events(self, event):
        # Jika popup aktif, alihkan semua event ke popup
        if self.show_popup:
            self.difficulty_popup.handle_event(event)
        else:
            # Jika tidak, tangani event untuk tombol menu utama
            for btn in self.main_buttons:
                btn.handle_event(event)

    def update(self, delta_time):
        pass # Tidak ada animasi di menu untuk saat ini

    def draw(self, surface):
        # 1. Gambar Menu Utama (Background)
        if self.menu_image:
            surface.blit(self.menu_image, (0, 0))
        else:
            surface.fill(self.bg_color)
            # Jika tidak ada gambar, mungkin perlu nambah teks judul sementara
            # title = self.difficulty_popup.font_title.render("FUNO GAME", True, COLOR_WHITE)
            # surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        # Debug hitbox tombol utama
        for btn in self.main_buttons:
            btn.draw(surface, debug=False) 

        # 2. Gambar Popup di atasnya (Jika aktif)
        if self.show_popup:
            self.difficulty_popup.draw(surface)