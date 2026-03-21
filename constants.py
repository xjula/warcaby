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

FONT_TITLE = pygame.font.SysFont('arial', 80, bold=True)
FONT_BUTTON = pygame.font.SysFont('arial', 24, bold=True)
FONT_INFO = pygame.font.SysFont('arial', 30, bold=True)