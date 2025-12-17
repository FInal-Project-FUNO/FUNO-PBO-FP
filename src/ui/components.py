import pygame

class Button:
    def __init__(self, x, y, width, height, action=None):
        # Kita hanya butuh Rect untuk posisi dan ukuran (Hitbox)
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.is_hovered = False

    def handle_event(self, event):
        # Deteksi Hover (Opsional, berguna jika ingin mengubah kursor mouse)
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        # Deteksi Klik
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Klik Kiri
                if self.rect.collidepoint(event.pos) and self.action:
                    self.action()

    def draw(self, surface, debug=False):
        # Secara default, tidak menggambar apa-apa (invisible)
        # Parameter debug=True bisa dipakai untuk melihat posisi hitbox saat development
        if debug:
            color = (255, 0, 0) if self.is_hovered else (0, 255, 0)
            pygame.draw.rect(surface, color, self.rect, 2) # Gambar garis tepi saja