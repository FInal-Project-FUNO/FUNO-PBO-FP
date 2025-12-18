import pygame
import sys
from .base import BaseScreen
from ..utils.constants import *
from ..ui.components import Button 

# --- CLASS TAMBAHAN UNTUK POPUP ---
class DifficultyPopup:
    """Helper class untuk menangani tampilan dan logika popup difficulty"""
    
    # UPDATE: Terima parameter sound dari luar
    def __init__(self, manager, on_close_callback, sound=None):
        self.manager = manager
        self.on_close = on_close_callback 
        self.click_sound = sound # Simpan referensi sound
        
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
            ("KID", "medium", (255, 213, 0)),   # Kuning
            ("MAN", "hard", (223, 50, 19))      # Merah 
        ]

        self.buttons = []
        for i, data in enumerate(self.button_data):
            label, diff_value, color = data
            action = lambda v=diff_value: self.set_difficulty(v)
            
            btn_rect = pygame.Rect(center_x, start_y + i*(btn_h+gap), btn_w, btn_h)
            self.buttons.append({
                'rect': btn_rect,
                'label': label,
                'color': color,
                'hitbox': Button(btn_rect.x, btn_rect.y, btn_w, btn_h, action=action)
            })

    def set_difficulty(self, level):
        # FIX: Mainkan sound disini (sekarang sudah aman karena sound dikirim dari MainMenu)
        if self.click_sound:
            self.click_sound.play()
            
        print(f"[Popup] Difficulty changed to: {level}")
        
        # Simpan setting ke manager agar bisa dibaca GameScreen
        self.manager.selected_difficulty = level
        
        # Tutup popup setelah memilih
        self.on_close()

    def handle_event(self, event):
        for btn_data in self.buttons:
            btn_data['hitbox'].handle_event(event)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.on_close()

    def draw(self, surface):
        # 1. Overlay Gelap
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 2. Panel Popup
        panel_color = (60, 60, 80) 
        border_color = (200, 200, 200)
        pygame.draw.rect(surface, (30, 30, 30), self.rect.move(5, 5), border_radius=15)
        pygame.draw.rect(surface, panel_color, self.rect, border_radius=15)
        pygame.draw.rect(surface, border_color, self.rect, 4, border_radius=15)

        # 3. Judul Popup
        title_surf = self.font_title.render("DIFFICULTY", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.x + self.width//2, self.y + 60))
        surface.blit(title_surf, title_rect)

        # 4. Gambar Tombol
        mouse_pos = pygame.mouse.get_pos()
        for btn_data in self.buttons:
            rect = btn_data['rect']
            base_color = btn_data['color']
            label = btn_data['label']

            draw_color = base_color
            if rect.collidepoint(mouse_pos):
                draw_color = [min(c + 30, 255) for c in base_color]
            
            pygame.draw.rect(surface, draw_color, rect, border_radius=8)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=8)

            text_surf = self.font_btn.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center) 
            text_rect.y -= 5
            
            shadow_surf = self.font_btn.render(label, True, (0, 0, 0))
            surface.blit(shadow_surf, text_rect.move(2, 2))
            surface.blit(text_surf, text_rect)


# --- MAIN MENU SCREEN CLASS ---
class MainMenu(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)
        
        # 1. LOAD SOUND (Lakukan ini di awal agar bisa dipakai Popup)
        self.click_sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.click_sound = pygame.mixer.Sound(SOUND_BUTTON_CLICK)
            self.click_sound.set_volume(0.7)
        except Exception as e:
            print(f"[WARNING] Menu sound error: {e}")

        # 2. Setup Background
        try:
            self.menu_image = pygame.image.load(MENU_PATH).convert()
            self.menu_image = pygame.transform.scale(self.menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"[WARNING] Menu image not found: {e}")
            self.menu_image = None
            self.bg_color = (40, 40, 50)

        # 3. Setup Tombol
        center_x = SCREEN_WIDTH // 2
        start_y = 250 
        btn_w, btn_h = 200, 50
        gap = 80

        self.main_buttons = [
            Button(center_x - btn_w//2, start_y, btn_w, btn_h, action=self.action_play),
            Button(center_x - btn_w//2, start_y + gap, btn_w, btn_h, action=self.action_open_difficulty),
            Button(center_x - btn_w//2, start_y + gap*2, btn_w, btn_h, action=self.action_exit)
        ]

        # 4. Setup Popup (Kirim sound ke sini!)
        self.show_popup = False
        self.difficulty_popup = DifficultyPopup(self.manager, self.close_popup, sound=self.click_sound)

    # --- Actions ---
    def action_play(self):
        if self.click_sound: self.click_sound.play()
        self.manager.set_screen('GAME')

    def action_open_difficulty(self):
        if self.click_sound: self.click_sound.play()
        self.show_popup = True

    def action_exit(self):
        if self.click_sound: self.click_sound.play()
        pygame.time.delay(200)
        pygame.quit()
        sys.exit()

    def close_popup(self):
        self.show_popup = False

    # --- Core Logic ---
    def handle_events(self, event):
        if self.show_popup:
            self.difficulty_popup.handle_event(event)
        else:
            for btn in self.main_buttons:
                btn.handle_event(event)

    def update(self, delta_time):
        pass

    def draw(self, surface):
        if self.menu_image:
            surface.blit(self.menu_image, (0, 0))
        else:
            surface.fill(self.bg_color)

        # Gambar Hitbox (Debug Only: set True jika ingin melihat kotak hijau/merah)
        for btn in self.main_buttons:
            btn.draw(surface, debug=False) 

        if self.show_popup:
            self.difficulty_popup.draw(surface)