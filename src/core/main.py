"""
Main game loop - Entry point
This is a simplified version showing the structure
"""

import pygame
import sys
from src.core import *
from src.utils import *
from .game_manager import GameManager

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