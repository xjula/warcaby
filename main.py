import sys

from constants import *
from ui import Button, IconButton
from board import GameBoard

pygame.init()

current_w = WIDTH
current_h = HEIGHT
is_fullscreen = False

SCREEN = pygame.display.set_mode((current_w, current_h))
pygame.display.set_caption("Warcaby - Projekt")

# Globalne zmienne dla obiektów UI
btn_2_players = btn_vs_pc = btn_online = btn_stats = btn_settings = None
btn_res_small = btn_res_large = btn_fullscreen = btn_back = None
main_board = None


def init_ui():
    """Funkcja przeliczająca i układająca wszystkie przyciski na nowo względem obecnego rozmiaru okna."""
    global btn_2_players, btn_vs_pc, btn_online, btn_stats, btn_settings
    global btn_res_small, btn_res_large, btn_fullscreen, btn_back
    global main_board

    btn_w, btn_h = 320, 65
    btn_x = (current_w - btn_w) // 2
    start_y = current_h // 2 - 50

    # Menu główne
    btn_2_players = Button(btn_x, start_y, btn_w, btn_h, "2 graczy")
    btn_vs_pc = Button(btn_x, start_y + 90, btn_w, btn_h, "Gra z komputerem")
    btn_online = Button(btn_x, start_y + 180, btn_w, btn_h, "Gra online")

    # Obliczanie kafelków dla prawego dolnego rogu
    icon_x = current_w - (current_w // 12)
    icon_y_settings = current_h - (current_h // 8)
    icon_y_stats = current_h - 3 * (current_h // 8)

    btn_stats = IconButton(icon_x, icon_y_stats, 80, "medal.png", "M")
    btn_settings = IconButton(icon_x, icon_y_settings, 80, "settings.png", "U")

    # Ustawienia (rozdzielczości)
    btn_res_small = Button(btn_x, start_y, btn_w, btn_h, "Małe okno (900x600)")
    btn_res_large = Button(btn_x, start_y + 90, btn_w, btn_h, "Duże okno (1280x720)")
    btn_fullscreen = Button(btn_x, start_y + 180, btn_w, btn_h, "Pełny ekran")

    btn_back = Button(20, 20, 150, 50, "Powrót")

    main_board = GameBoard(current_w, current_h)


def set_resolution(w, h, fullscreen=False):
    """Zmienia wielkość okna i odpala przeliczenie interfejsu."""
    global current_w, current_h, is_fullscreen, SCREEN
    is_fullscreen = fullscreen

    if fullscreen:
        SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        current_w, current_h = SCREEN.get_size()  # Pobieramy faktyczny rozmiar ekranu
    else:
        current_w, current_h = w, h
        SCREEN = pygame.display.set_mode((current_w, current_h))

    init_ui()


# --- FUNKCJE RYSUJĄCE GŁÓWNE EKRANY ---
def draw_checkered_background(surface):
    cols, rows = 6, 4
    sw, sh = current_w // cols, current_h // rows
    surface.fill(WHITE)
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 != 0:
                pygame.draw.rect(surface, SQUARE_COLOR, (c * sw, r * sh, sw, sh))


def draw_menu():
    draw_checkered_background(SCREEN)
    title_surf = FONT_TITLE.render("WARCABY", True, BLACK)
    title_rect = title_surf.get_rect(center=(current_w // 2, current_h * 0.15))
    bg_rect = pygame.Rect(title_rect.x - 50, title_rect.y - 10, title_rect.width + 100, title_rect.height + 20)

    pygame.draw.rect(SCREEN, SHADOW_COLOR, bg_rect.move(0, 6), border_radius=40)
    pygame.draw.rect(SCREEN, WHITE, bg_rect, border_radius=40)
    SCREEN.blit(title_surf, title_rect)

    btn_2_players.draw(SCREEN)
    btn_vs_pc.draw(SCREEN)
    btn_online.draw(SCREEN)
    btn_stats.draw(SCREEN)
    btn_settings.draw(SCREEN)


def draw_settings():
    SCREEN.fill(SQUARE_COLOR)
    title_surf = FONT_TITLE.render("USTAWIENIA", True, WHITE)
    SCREEN.blit(title_surf, (current_w // 2 - title_surf.get_width() // 2, 50))

    btn_res_small.draw(SCREEN)
    btn_res_large.draw(SCREEN)
    btn_fullscreen.draw(SCREEN)
    btn_back.draw(SCREEN)


def draw_game_screen(board_obj):
    SCREEN.fill((210, 220, 222))
    btn_back.draw(SCREEN)

    # Dynamiczny napis tury
    color_name = "Czerwone" if board_obj.turn == 1 else "Białe"
    turn_surf = FONT_INFO.render(f"Tura: Gracz {board_obj.turn} ({color_name})", True, BLACK)
    SCREEN.blit(turn_surf, (current_w // 2 - turn_surf.get_width() // 2, 20))

    board_obj.draw(SCREEN)

    winner = board_obj.check_winner()
    if winner:
        # Wybieramy tekst i kolor
        winner_text = "WYGRYWA CZERWONY!" if winner == 1 else "WYGRYWA BIAŁY!"
        text_color = (200, 0, 0) if winner == 1 else (50, 50, 50)

        # Generujemy napis
        msg_surf = FONT_TITLE.render(winner_text, True, text_color)

        # Tworzymy tło, żeby napis był widoczny na środku szachownicy
        bg_rect = msg_surf.get_rect(center=(current_w // 2, current_h // 2))
        pygame.draw.rect(SCREEN, WHITE, bg_rect.inflate(40, 20), border_radius=20)
        pygame.draw.rect(SCREEN, BLACK, bg_rect.inflate(40, 20), width=3, border_radius=20)

        # Rysujemy napis
        SCREEN.blit(msg_surf, bg_rect)


def draw_temp_ui(title_text):
    SCREEN.fill(SQUARE_COLOR)
    btn_back.draw(SCREEN)
    SCREEN.blit(FONT_INFO.render(title_text, True, WHITE), (20, 100))


# --- GŁÓWNA PĘTLA GRY ---
main_board = GameBoard(WIDTH, HEIGHT) # Inicjalizacja raz na start
def main():
    clock = pygame.time.Clock()
    state = "MENU"

    init_ui()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Globalna obsługa klawisza ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state != "MENU":
                    state = "MENU"

            # Obsługa kliknięć w zależności od obecnego ekranu
            if state == "MENU":
                if btn_2_players.is_clicked(event):
                    state = "GAME_2P"
                    main_board.create_starting_board()  # Reset planszy
                elif btn_vs_pc.is_clicked(event):
                    state = "GAME_PC"
                elif btn_online.is_clicked(event):
                    state = "GAME_ONLINE"
                elif btn_stats.is_clicked(event):
                    state = "STATS"
                elif btn_settings.is_clicked(event):
                    state = "SETTINGS"

            elif state == "SETTINGS":
                if btn_back.is_clicked(event):
                    state = "MENU"
                elif btn_res_small.is_clicked(event):
                    set_resolution(900, 600)
                elif btn_res_large.is_clicked(event):
                    set_resolution(1280, 720)
                elif btn_fullscreen.is_clicked(event):
                    set_resolution(0, 0, fullscreen=True)

            elif state == "GAME_2P":

                if btn_back.is_clicked(event):
                    state = "MENU"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    coords = main_board.get_clicked_pos(pos)
                    if coords:
                        main_board.select_piece(coords[0], coords[1])
                    else:
                        main_board.selected_piece = None
                        main_board.valid_moves = {}

            elif state in ["GAME_PC", "GAME_ONLINE", "STATS"]:
                if btn_back.is_clicked(event):
                    state = "MENU"

        if state == "MENU":
            draw_menu()
        elif state == "SETTINGS":
            draw_settings()
        elif state == "GAME_2P":
            draw_game_screen(main_board)
        elif state == "GAME_PC":
            draw_temp_ui("Tryb: Gra z Komputerem")
        elif state == "GAME_ONLINE":
            draw_temp_ui("Tryb: Gra Online")
        elif state == "STATS":
            draw_temp_ui("Ekran: Statystyki i Osiągnięcia")

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()