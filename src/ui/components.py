import pygame
from src.utils.constants import *

class Button:
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action # Fungsi yang akan dijalankan saat diklik
        
        # Warna (Bisa dipindah ke constants nanti)
        self.color_normal = COLOR_GRAY
        self.color_hover = COLOR_YELLOW
        self.text_color = COLOR_WHITE
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.action:
                self.action() # Panggil fungsi callback

    def draw(self, surface):
        # 1. Gambar Kotak (Background)
        color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, 3, border_radius=10) # Border

        # 2. Gambar Teks (Centered)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)