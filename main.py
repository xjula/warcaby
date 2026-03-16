import pygame
import sys
import os

# Inicjalizacja Pygame
pygame.init()

# --- USTAWIENIA OKNA I KOLORY ---
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warcaby - Projekt")

# Kolory UI
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SQUARE_COLOR = (135, 166, 168)
BUTTON_COLOR = (6, 75, 84)
BUTTON_HOVER = (10, 95, 105)
SHADOW_COLOR = (100, 120, 122)

# Kolory Gry (Plansza i Pionki)
BOARD_LIGHT = (240, 235, 225)
BOARD_DARK = (135, 166, 168)
PIECE_PLAYER_1 = (180, 50, 50)  # Czerwony
PIECE_PLAYER_2 = (245, 245, 235)  # Kremowy/Biały
PIECE_BORDER = (50, 50, 50)  # Ciemna obwódka dla kontrastu

# Czcionki
FONT_TITLE = pygame.font.SysFont('arial', 80, bold=True)
FONT_BUTTON = pygame.font.SysFont('arial', 24, bold=True)
FONT_INFO = pygame.font.SysFont('arial', 30, bold=True)


# --- KLASY POMOCNICZE (UI) ---
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR

        shadow_rect = self.rect.copy()
        shadow_rect.y += 5
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=30)
        pygame.draw.rect(surface, color, self.rect, border_radius=30)

        text_surf = FONT_BUTTON.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class IconButton:
    def __init__(self, center_x, center_y, size, image_filename, fallback_char):
        self.rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
        self.fallback_char = fallback_char
        self.image = None

        if os.path.exists(image_filename):
            try:
                img = pygame.image.load(image_filename).convert_alpha()
                self.image = pygame.transform.smoothscale(img, (size, size))
            except Exception as e:
                print(f"Błąd obrazka: {e}")

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        if is_hover:
            pygame.draw.circle(surface, SHADOW_COLOR, self.rect.center, self.rect.width // 2 + 5)

        if self.image:
            surface.blit(self.image, self.rect)
        else:
            color = BUTTON_HOVER if is_hover else BUTTON_COLOR
            pygame.draw.circle(surface, color, self.rect.center, self.rect.width // 2)
            text_surf = FONT_BUTTON.render(self.fallback_char, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# --- KLASA PLANSZY GRY ---
class GameBoard:
    def __init__(self):
        self.rows = 8
        self.cols = 8
        self.square_size = 65  # Rozmiar pojedynczego pola na planszy

        # Obliczamy pozycję X i Y, aby plansza była wyśrodkowana na ekranie
        self.board_width = self.cols * self.square_size
        self.board_height = self.rows * self.square_size
        self.start_x = (WIDTH - self.board_width) // 2
        self.start_y = (HEIGHT - self.board_height) // 2 + 20  # Lekko opuszczona

        self.board_state = []
        self.create_starting_board()

    def create_starting_board(self):
        """Wypełnia planszę początkowym ustawieniem pionków (0 - puste, 1 - gracz 1, 2 - gracz 2)."""
        for row in range(self.rows):
            self.board_state.append([])
            for col in range(self.cols):
                # Pionki mogą stać tylko na ciemnych polach
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board_state[row].append(2)  # Pionki z góry (Gracz 2)
                    elif row > 4:
                        self.board_state[row].append(1)  # Pionki z dołu (Gracz 1)
                    else:
                        self.board_state[row].append(0)  # Puste ciemne pole
                else:
                    self.board_state[row].append(0)  # Jasne pole

    def draw(self, surface):
        """Rysuje szachownicę i pionki."""
        # 1. Rysowanie pól planszy
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * self.square_size
                y = self.start_y + row * self.square_size

                # Zmiana koloru co drugie pole
                color = BOARD_DARK if col % 2 == ((row + 1) % 2) else BOARD_LIGHT
                pygame.draw.rect(surface, color, (x, y, self.square_size, self.square_size))

        # 2. Rysowanie pionków na podstawie stanu (self.board_state)
        radius = self.square_size // 2 - 8  # Promień pionka z marginesem
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board_state[row][col]
                if piece != 0:
                    center_x = self.start_x + col * self.square_size + self.square_size // 2
                    center_y = self.start_y + row * self.square_size + self.square_size // 2

                    piece_color = PIECE_PLAYER_1 if piece == 1 else PIECE_PLAYER_2

                    # Rysujemy główny kolor pionka, a potem ciemną obwódkę
                    pygame.draw.circle(surface, piece_color, (center_x, center_y), radius)
                    pygame.draw.circle(surface, PIECE_BORDER, (center_x, center_y), radius, 3)
                    # Wewnętrzne ozdobne kółko
                    pygame.draw.circle(surface, PIECE_BORDER, (center_x, center_y), radius - 8, 1)


# --- FUNKCJE RYSUJĄCE GŁÓWNE EKRANY ---
def draw_checkered_background(surface):
    cols, rows = 6, 4
    sw, sh = WIDTH // cols, HEIGHT // rows
    surface.fill(WHITE)
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 != 0:
                pygame.draw.rect(surface, SQUARE_COLOR, (c * sw, r * sh, sw, sh))


def draw_menu():
    draw_checkered_background(SCREEN)
    title_surf = FONT_TITLE.render("WARCABY", True, BLACK)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 100))
    bg_rect = pygame.Rect(title_rect.x - 50, title_rect.y - 10, title_rect.width + 100, title_rect.height + 20)

    pygame.draw.rect(SCREEN, SHADOW_COLOR, bg_rect.move(0, 6), border_radius=40)
    pygame.draw.rect(SCREEN, WHITE, bg_rect, border_radius=40)
    SCREEN.blit(title_surf, title_rect)

    btn_2_players.draw(SCREEN)
    btn_vs_pc.draw(SCREEN)
    btn_online.draw(SCREEN)
    btn_stats.draw(SCREEN)
    btn_settings.draw(SCREEN)


def draw_game_screen(board_obj):
    """Odpowiada za widok właściwej gry."""
    SCREEN.fill((210, 220, 222))  # Jednolite, spokojne tło dla ekranu gry

    # Informacja o turze (na razie na sztywno, zmienimy to później)
    turn_surf = FONT_INFO.render("Tura: Gracz 1 (Czerwone)", True, PIECE_PLAYER_1)
    SCREEN.blit(turn_surf, (WIDTH // 2 - turn_surf.get_width() // 2, 20))

    # Rysujemy właściwą planszę z pionkami
    board_obj.draw(SCREEN)


def draw_temp_ui(title_text):
    SCREEN.fill(SQUARE_COLOR)
    SCREEN.blit(FONT_INFO.render(title_text, True, WHITE), (20, 20))
    SCREEN.blit(FONT_INFO.render("Wciśnij ESC, aby wrócić do Menu", True, WHITE), (20, 60))


# --- TWORZENIE OBIEKTÓW ---
btn_x = (WIDTH - 320) // 2
btn_2_players = Button(btn_x, 220, 320, 65, "2 graczy")
btn_vs_pc = Button(btn_x, 310, 320, 65, "Gra z komputerem")
btn_online = Button(btn_x, 400, 320, 65, "Gra online")
btn_stats = IconButton(825, 375, 80, "medal.png", "M")
btn_settings = IconButton(825, 525, 80, "settings.png", "U")

# Obiekt planszy
main_board = GameBoard()


# --- GŁÓWNA PĘTLA GRY ---
def main():
    clock = pygame.time.Clock()
    state = "MENU"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "MENU":
                if btn_2_players.is_clicked(event):
                    state = "GAME_2P"
                    main_board = GameBoard()  # Reset planszy po wejściu w tryb 2 graczy
                elif btn_vs_pc.is_clicked(event):
                    state = "GAME_PC"
                elif btn_online.is_clicked(event):
                    state = "GAME_ONLINE"
                elif btn_stats.is_clicked(event):
                    state = "STATS"
                elif btn_settings.is_clicked(event):
                    state = "SETTINGS"

            else:
                # Wyjście z gry klawiszem ESC
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "MENU"



        # Renderowanie odpowiedniego ekranu
        if state == "MENU":
            draw_menu()
        elif state == "GAME_2P":
            draw_game_screen(main_board)
        elif state == "GAME_PC":
            draw_temp_ui("Tryb: Gra z Komputerem")
        elif state == "GAME_ONLINE":
            draw_temp_ui("Tryb: Gra Online")
        elif state == "STATS":
            draw_temp_ui("Ekran: Statystyki i Osiągnięcia")
        elif state == "SETTINGS":
            draw_temp_ui("Ekran: Ustawienia")

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()