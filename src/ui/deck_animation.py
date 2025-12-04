import pygame
from src.core import *
from src.utils import *
from src.core.game_manager import GameManager

def load_deck_sprites(sheet_path, num_frames):
    """
    Memuat sprite sheet dan memotongnya menjadi list frame.
    Mengembalikan list berisi Surface pygame untuk setiap frame.
    """
    sprites = []
    try:
        sheet = pygame.image.load(sheet_path).convert_alpha() # convert_alpha agar transparan rapi
        sheet_width, sheet_height = sheet.get_size()
        
        # Hitung lebar satu frame (Total Lebar / Jumlah Frame)
        frame_width = sheet_width // num_frames
        
        for i in range(num_frames):
            # Tentukan area potong (Rect) untuk frame ke-i
            # (x, y, width, height)
            rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
            
            # Ambil potongan gambar (subsurface)
            frame = sheet.subsurface(rect)
            
            # Scale frame agar sesuai ukuran kartu di game
            scaled_frame = pygame.transform.scale(frame, (CARD_WIDTH, CARD_HEIGHT))
            sprites.append(scaled_frame)
            
        return sprites
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"[ERROR] Gagal memuat deck sprite: {e}")
        return []

# --- LOAD SPRITES DI TINGKAT GLOBAL ---
# Panggil fungsi ini di luar loop main() agar hanya diload sekali
deck_frames = load_deck_sprites(DECK_IMAGES, 5) # Asumsi DECK_IMAGES dari constants sudah dipath ke file png
    
DECK_SURFACE = None
try:
    img = pygame.image.load(DECK_IMAGES)
    DECK_SURFACE = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
except (FileNotFoundError, NameError) as e:
    print(f" Gagal memuat gambar deck: {e}")    
    
def load_deck(surface, x, y, current_cards_count):
    """Draw deck image to game screen"""
# Cek apakah sprite berhasil di-load
    if not deck_frames:
        # Fallback: gambar kotak biasa jika gambar gagal load
        pygame.draw.rect(surface, COLOR_GRAY, (x, y, CARD_WIDTH, CARD_HEIGHT))
        return

    # 1. Tentukan frame mana yang dipakai
    frame_index = get_deck_frame_index(current_cards_count, MAX_DECK_SIZE)
    
    # 2. Ambil gambarnya
    image = deck_frames[frame_index]
    
    # 3. Gambar ke layar
    rect = image.get_rect(topleft=(x, y))
    surface.blit(image, rect)
# src/main.py

def get_deck_frame_index(current_count, max_count=60):
    """
    Menghitung index frame berdasarkan persentase sisa kartu.
    """
    if current_count <= 0:
        return 4 # Frame terakhir (paling tipis/habis)
    
    if current_count >= max_count:
        return 0 # Frame pertama (paling tebal)

    # Hitung persentase kartu tersisa (0.0 sampai 1.0)
    percent = current_count / max_count
    
    # Balik logikanya: 
    # 100% kartu -> index 0
    # 0% kartu -> index 4
    # Rumus: (Total Frame - 1) - (Persen * (Total Frame - 1))
    total_frames = 5
    index = int((total_frames - 1) - (percent * (total_frames - 1)))
    
    # Pastikan index tidak keluar batas (clamping)
    return max(0, min(index, total_frames - 1))