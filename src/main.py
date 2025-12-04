"""
Main game loop - Entry point
This is a simplified version showing the structure
"""

import pygame
import sys
from src.core import *
from src.utils import *
from src.core.game_manager import GameManager

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FUNO - Fast UNO Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Load semua gambar dan scale ke ukuran kartu
LOADED_CARDS = {}
for name, path in CARD_IMAGES.items():
    try:
        img = pygame.image.load(path)
        LOADED_CARDS[name] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
    except FileNotFoundError:
        print(f"[WARNING] File tidak ditemukan: {path}")

def draw_card_image(surface, card, x, y, selected=False):
    """Draw a card using its image, matching based on color and value"""
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
        if key in LOADED_CARDS:
            image = LOADED_CARDS[key]
            break
    if image is None:
        image = LOADED_CARDS.get("back")

    rect = image.get_rect(topleft=(x, y))

    if selected:
        pygame.draw.rect(surface, COLOR_YELLOW, rect.inflate(4, 4), 3)

    surface.blit(image, rect)
    
    
# src/main.py

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
    

def main():
    """Main game function"""
    game = GameManager()
    selected_card_index = None
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                # Handle card selection
                mouse_x, mouse_y = event.pos
                
                # Check player cards
                player_cards = game.player.hand
                for i, card in enumerate(player_cards):
                    card_x = 50 + i * (CARD_WIDTH + 10)
                    card_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
                    
                    if (card_x <= mouse_x <= card_x + CARD_WIDTH and
                        card_y <= mouse_y <= card_y + CARD_HEIGHT):
                        
                        # Try to play card
                        try:
                            game.play_card(game.player, card)
                            selected_card_index = None
                        except (InvalidMoveError, InvalidCardError) as e:
                            game._GameManager__message = str(e)
        
        # Update AI
        if not game.game_over:
            game.update_ai()
        
        # Drawing
        screen.fill(COLOR_DARK_GREEN)
        
        cards_left = game.deck.cards_remaining()
        #draw deck
        load_deck(screen, 250, SCREEN_HEIGHT//2.3,cards_left)    
        
            
        # Draw main card
        if game.main_card:
            main_x = SCREEN_WIDTH // 2 - CARD_WIDTH // 2
            main_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
            draw_card_image(screen, game.main_card, main_x, main_y)
            
            label = small_font.render("MAIN CARD", True, COLOR_WHITE)
            screen.blit(label, (main_x, main_y - 30))
        
        # Draw player cards
        player_cards = game.player.hand
        for i, card in enumerate(player_cards):
            card_x = 50 + i * (CARD_WIDTH + 10)
            card_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
            draw_card_image(screen, card, card_x, card_y, i == selected_card_index)
        
        # Draw AI cards (back side)
        ai_cards_count = game.ai.hand_size()
        for i in range(ai_cards_count):
            card_x = 50 + i * (CARD_WIDTH + 10)
            card_y = 30
            
            back_image = LOADED_CARDS.get("back")
            if back_image:
                screen.blit(back_image, (card_x, card_y))
            else:
                # fallback kalau gambar back tidak ada
                pygame.draw.rect(screen, COLOR_GRAY, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))
                pygame.draw.rect(screen, COLOR_BLACK, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT), 3)
        
        # Draw scores
        player_score_text = font.render(f"Your Score: {game.player.score}", True, COLOR_WHITE)
        ai_score_text = font.render(f"AI Score: {game.ai.score}", True, COLOR_WHITE)
        deck_text = small_font.render(f"Deck: {game.deck.cards_remaining()}", True, COLOR_WHITE)
        
        screen.blit(player_score_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100))
        screen.blit(ai_score_text, (SCREEN_WIDTH - 250, 50))
        screen.blit(deck_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2))
        
        # Draw message
        if game.message:
            msg_text = small_font.render(game.message, True, COLOR_YELLOW)
            screen.blit(msg_text, (50, SCREEN_HEIGHT // 2 - 100))
        
        # Draw game over screen
        if game.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))
            
            if game.winner:
                winner_text = font.render(f"{game.winner.name} WINS!", True, COLOR_YELLOW)
            else:
                winner_text = font.render("IT'S A TIE!", True, COLOR_YELLOW)
            
            final_score = font.render(
                f"Final Score - You: {game.player.score} | AI: {game.ai.score}",
                True, COLOR_WHITE
            )
            
            restart_text = small_font.render("Press ESC to exit", True, COLOR_WHITE)
            
            screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 250))
            screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, 350))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 450))
            
            # Allow exit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()