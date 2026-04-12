import pygame

pygame.font.init()

# --- USTAWIENIA OKNA I KOLORY ---
WIDTH, HEIGHT = 900, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SQUARE_COLOR = (135, 166, 168)
BUTTON_COLOR = (6, 75, 84)
BUTTON_HOVER = (10, 95, 105)
SHADOW_COLOR = (100, 120, 122)

BOARD_LIGHT = (240, 235, 225)
BOARD_DARK = (135, 166, 168)
PIECE_PLAYER_1 = (180, 50, 50)
PIECE_PLAYER_2 = (245, 245, 235)
PIECE_BORDER = (50, 50, 50)

GOLD = BOARD_LIGHT
ACCENT_COLOR = SQUARE_COLOR
CARD_BG = BUTTON_COLOR

class Fonts:
    title = None
    button = None
    info = None
    small = None

def update_fonts(scale):
    Fonts.title = pygame.font.SysFont('arial', max(20, int(80 * scale)), bold=True)
    Fonts.button = pygame.font.SysFont('arial', max(12, int(24 * scale)), bold=True)
    Fonts.info = pygame.font.SysFont('arial', max(14, int(30 * scale)), bold=True)
    Fonts.small = pygame.font.SysFont('arial', max(10, int(20 * scale)), bold=True)