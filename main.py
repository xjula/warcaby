import sys
import json
import os

from constants import *
from ui import Button, IconButton
from board import GameBoard
from ai import get_best_move
from network import Network

pygame.init()

current_w = WIDTH
current_h = HEIGHT
is_fullscreen = False
SAVE_FILE = "current_game.json"

SCREEN = pygame.display.set_mode((current_w, current_h))
pygame.display.set_caption("Warcaby - Projekt")

# Globalne zmienne dla obiektów UI
btn_2_players = btn_vs_pc = btn_online = btn_stats = btn_settings = None
btn_res_small = btn_res_large = btn_fullscreen = btn_back = None
btn_poddaj = btn_zapisz = None
main_board = None

net = None
my_id = None

def init_ui():
    """Funkcja przeliczająca i układająca wszystkie przyciski na nowo względem obecnego rozmiaru okna."""
    global btn_2_players, btn_vs_pc, btn_online, btn_stats, btn_settings
    global btn_res_small, btn_res_large, btn_fullscreen, btn_back, btn_poddaj, btn_zapisz
    global main_board

    BASE_W, BASE_H = 900, 600
    scale = min(current_w / BASE_W, current_h / BASE_H)
    update_fonts(scale)

    btn_w = int(320 * scale)
    btn_h = int(65 * scale)
    btn_spacing = int(90 * scale)

    btn_x = (current_w - btn_w) // 2
    start_y = current_h // 2 - int(50 * scale)

    # Menu główne
    btn_2_players = Button(btn_x, start_y, btn_w, btn_h, "2 graczy")
    btn_vs_pc = Button(btn_x, start_y + btn_spacing, btn_w, btn_h, "Gra z komputerem")
    btn_online = Button(btn_x, start_y + (btn_spacing * 2), btn_w, btn_h, "Gra online")

    # Obliczanie kafelków dla prawego dolnego rogu
    icon_size = int(80 * scale)
    icon_x = current_w - (current_w // 12)
    icon_y_settings = current_h - (current_h // 8)
    icon_y_stats = current_h - 3 * (current_h // 8)

    btn_stats = IconButton(icon_x, icon_y_stats, icon_size, "medal.png", "M")
    btn_settings = IconButton(icon_x, icon_y_settings, icon_size, "settings.png", "U")

    # Ustawienia
    btn_res_small = Button(btn_x, start_y, btn_w, btn_h, "Małe okno (900x600)")
    btn_res_large = Button(btn_x, start_y + btn_spacing, btn_w, btn_h, "Duże okno (1280x720)")
    btn_fullscreen = Button(btn_x, start_y + (btn_spacing * 2), btn_w, btn_h, "Pełny ekran")

    btn_back = Button(int(20 * scale), int(20 * scale), int(150 * scale), int(50 * scale), "Powrót")
    btn_poddaj = Button(int(20 * scale), current_h - int(50 * scale) - int(20 * scale), int(150 * scale), int(50 * scale), "Poddaj")
    btn_zapisz = Button(current_w - int(180 * scale) - int(20 * scale), current_h - int(50 * scale) - int(20 * scale), int(180 * scale), int(50 * scale), "Zapisz ruchy")

    main_board = GameBoard(current_w, current_h)

def set_resolution(w, h, fullscreen=False):
    """Zmienia wielkość okna i odpala przeliczenie interfejsu."""
    global current_w, current_h, is_fullscreen, SCREEN
    is_fullscreen = fullscreen

    if fullscreen:
        SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        current_w, current_h = SCREEN.get_size()
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
    title_surf = Fonts.title.render("WARCABY", True, BLACK)
    title_rect = title_surf.get_rect(center=(current_w // 2, current_h * 0.15))

    # Dynamiczne skalowanie tła pod tytułem
    scale = min(current_w / 900, current_h / 600)
    padding_w, padding_h = int(50 * scale), int(10 * scale)

    bg_rect = pygame.Rect(title_rect.x - padding_w, title_rect.y - padding_h,
                          title_rect.width + padding_w * 2, title_rect.height + padding_h * 2)

    pygame.draw.rect(SCREEN, SHADOW_COLOR, bg_rect.move(0, max(2, int(6*scale))), border_radius=int(40*scale))
    pygame.draw.rect(SCREEN, WHITE, bg_rect, border_radius=int(40*scale))
    SCREEN.blit(title_surf, title_rect)

    btn_2_players.draw(SCREEN)
    btn_vs_pc.draw(SCREEN)
    btn_online.draw(SCREEN)
    btn_stats.draw(SCREEN)
    btn_settings.draw(SCREEN)

def draw_settings():
    SCREEN.fill(SQUARE_COLOR)
    title_surf = Fonts.title.render("USTAWIENIA", True, WHITE)
    SCREEN.blit(title_surf, (current_w // 2 - title_surf.get_width() // 2, int(50 * min(current_w/900, current_h/600))))

    btn_res_small.draw(SCREEN)
    btn_res_large.draw(SCREEN)
    btn_fullscreen.draw(SCREEN)
    btn_back.draw(SCREEN)

def draw_game_screen(board_obj):
    SCREEN.fill((210, 220, 222))
    btn_back.draw(SCREEN)

    color_name = "Czerwone" if board_obj.turn == 1 else "Białe"
    turn_surf = Fonts.info.render(f"Tura: Gracz {board_obj.turn} ({color_name})", True, BLACK)
    SCREEN.blit(turn_surf, (current_w // 2 - turn_surf.get_width() // 2, int(20 * min(current_w/900, current_h/600))))

    board_obj.draw(SCREEN)

    winner = board_obj.check_winner()
    if winner:
        winner_text = "WYGRYWA CZERWONY!" if winner == 1 else "WYGRYWA BIAŁY!"
        text_color = (200, 0, 0) if winner == 1 else (50, 50, 50)

        msg_surf = Fonts.title.render(winner_text, True, text_color)

        scale = min(current_w / 900, current_h / 600)
        bg_rect = msg_surf.get_rect(center=(current_w // 2, current_h // 2))
        inflate_amount = int(40 * scale)
        border_rad = int(20 * scale)
        border_thick = max(1, int(3 * scale))

        pygame.draw.rect(SCREEN, WHITE, bg_rect.inflate(inflate_amount, inflate_amount//2), border_radius=border_rad)
        pygame.draw.rect(SCREEN, BLACK, bg_rect.inflate(inflate_amount, inflate_amount//2), width=border_thick, border_radius=border_rad)

        SCREEN.blit(msg_surf, bg_rect)

def draw_temp_ui(title_text):
    SCREEN.fill(SQUARE_COLOR)
    btn_back.draw(SCREEN)
    SCREEN.blit(Fonts.info.render(title_text, True, WHITE), (int(20 * (current_w/900)), int(100 * (current_h/600))))

# --- LOGIKA STATYSTYK ---
STATS_FILE = "stats.json"


def load_stats():
    # Oczekiwana nowa struktura
    default_stats = {
        "games_played": 0,
        "kings_created": 0,
        "mode_2p": {"wins": 0, "losses": 0},
        "mode_pc": {"wins": 0, "losses": 0},
        "mode_online": {"wins": 0, "losses": 0}
    }

    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                loaded_stats = json.load(f)

            # Proste zabezpieczenie przed starym formatem pliku:
            # Jeśli wczytany plik nie ma np. 'mode_2p', to nadpisujemy go domyślnym
            if "mode_2p" not in loaded_stats:
                print("Wykryto stary format statystyk. Tworzę nowy...")
                save_stats(default_stats)
                return default_stats

            return loaded_stats
        except json.JSONDecodeError:
            print("Błąd odczytu pliku stats.json. Używam domyślnych statystyk.")
            return default_stats

    return default_stats

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def draw_stats(stats):
    # Tło szachownicy
    draw_checkered_background(SCREEN)

    scale = min(current_w / 900, current_h / 600)

    # Nagłówek główny
    title_surf = Fonts.title.render("STATYSTYKI", True, BLACK)
    title_rect = title_surf.get_rect(center=(current_w // 2, int(60 * scale)))
    SCREEN.blit(title_surf, title_rect)

    # Wymiary do wyliczania pozycji kart
    margin = int(20 * scale)
    card_h = int(110 * scale)
    bottom_card_w = int(260 * scale)
    top_card_w = (bottom_card_w * 3) + (margin * 2)

    # KARTA GŁÓWNA ("OGÓLNE")
    top_x = (current_w - top_card_w) // 2
    top_y = int(110 * scale)

    top_rect = pygame.Rect(top_x, top_y, top_card_w, card_h)
    pygame.draw.rect(SCREEN, CARD_BG, top_rect, border_radius=int(12 * scale))

    sec_title_top = Fonts.button.render("OGÓLNE OSIĄGNIĘCIA", True, GOLD)
    SCREEN.blit(sec_title_top, (top_x + int(25 * scale), top_y + int(12 * scale)))

    # Statystyki ogólne obok siebie
    data_text_1 = f"Rozegrane partie: {stats['games_played']}"
    data_text_2 = f"Stworzone damki: {stats['kings_created']}"

    data_surf_1 = Fonts.info.render(data_text_1, True, WHITE)
    data_surf_2 = Fonts.info.render(data_text_2, True, WHITE)

    SCREEN.blit(data_surf_1, (top_x + int(40 * scale), top_y + int(55 * scale)))
    SCREEN.blit(data_surf_2, (top_x + top_card_w // 2 + int(20 * scale), top_y + int(55 * scale)))

    # TRZY MNIEJSZE KARTY Z TRYBAMI GRY
    sections_bottom = [
        {
            "title": "2 GRACZY",
            "data": [f"Wygrane P1: {stats['mode_2p']['wins']}", f"Wygrane P2: {stats['mode_2p']['losses']}"]
        },
        {
            "title": "KOMPUTER",
            "data": [f"Wygrane: {stats['mode_pc']['wins']}", f"Przegrane: {stats['mode_pc']['losses']}"]
        },
        {
            "title": "ONLINE",
            "data": [f"Wygrane P1: {stats['mode_online']['wins']}", f"Wygrane P2: {stats['mode_online']['losses']}"]
        }
    ]

    bottom_start_y = top_y + card_h + int(30 * scale)
    bottom_start_x = top_x

    for i, section in enumerate(sections_bottom):
        x = bottom_start_x + i * (bottom_card_w + margin)
        y = bottom_start_y

        card_rect = pygame.Rect(x, y, bottom_card_w, card_h)
        # Tło karty
        pygame.draw.rect(SCREEN, CARD_BG, card_rect, border_radius=int(12 * scale))

        sec_title = Fonts.button.render(section['title'], True, GOLD)
        SCREEN.blit(sec_title, (x + int(20 * scale), y + int(12 * scale)))

        for j, line in enumerate(section['data']):
            data_surf = Fonts.small.render(line, True, WHITE)
            SCREEN.blit(data_surf, (x + int(20 * scale), y + int(45 * scale) + j * int(22 * scale)))

    # Przycisk powrotu
    btn_back.draw(SCREEN)

def save_current_game(board):
    with open(SAVE_FILE, "w") as f:
        json.dump(board.get_save_data(), f)

def load_saved_game(board, target_mode):
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data.get("mode") == target_mode:
                board.load_save_data(data)
                return True
    return False


# --- GŁÓWNA PĘTLA GRY ---
main_board = GameBoard(WIDTH, HEIGHT)  # Inicjalizacja raz na start


def main():
    global net, my_id  # Deklaracja globalna, by móc modyfikować te zmienne wewnątrz funkcji

    ai_timer = 0
    clock = pygame.time.Clock()
    state = "MENU"

    init_ui()

    # Ładujemy statystyki TYLKO RAZ przy uruchomieniu gry
    stats = load_stats()
    game_recorded = False  # Inicjacja flagi przed pętlą

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
                    main_board.current_state = "GAME_2P"
                    if not load_saved_game(main_board, "GAME_2P"):
                        main_board.create_starting_board()
                    state = "GAME_2P"
                    game_recorded = False
                elif btn_vs_pc.is_clicked(event):
                    main_board.current_state = "GAME_PC"
                    if not load_saved_game(main_board, "GAME_PC"):
                        main_board.create_starting_board()
                    state = "GAME_PC"
                    game_recorded = False
                elif btn_online.is_clicked(event):
                    net = Network()
                    my_id = net.player_id
                    state = "GAME_ONLINE"
                    main_board.create_starting_board()
                    game_recorded = False
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
                    winner = main_board.check_winner()

                    if winner:
                        main_board.create_starting_board()
                        if os.path.exists(SAVE_FILE):
                            os.remove(SAVE_FILE)
                    else:
                        save_current_game(main_board)

                    state = "MENU"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    coords = main_board.get_clicked_pos(pos)
                    if coords:
                        main_board.select_piece(coords[0], coords[1])
                    else:
                        main_board.selected_piece = None
                        main_board.valid_moves = {}

            elif state == "GAME_PC":
                if btn_back.is_clicked(event):
                    winner = main_board.check_winner()

                    if winner:
                        main_board.create_starting_board()
                        if os.path.exists(SAVE_FILE):
                            os.remove(SAVE_FILE)
                    else:
                        save_current_game(main_board)

                    state = "MENU"

                if event.type == pygame.MOUSEBUTTONDOWN and main_board.turn == 1:
                    pos = pygame.mouse.get_pos()
                    coords = main_board.get_clicked_pos(pos)
                    if coords:
                        main_board.select_piece(coords[0], coords[1])
                    else:
                        main_board.selected_piece = None
                        main_board.valid_moves = {}

            elif state == "STATS":
                if btn_back.is_clicked(event):
                    state = "MENU"

            elif state == "GAME_ONLINE":
                # Wysyłanie własnego ruchu
                if btn_back.is_clicked(event):
                    if net:
                        net.disconnect()
                    state = "MENU"
                    main_board.selected_piece = None
                    main_board.valid_moves = {}
                    main_board.must_continue_jump = False

                if event.type == pygame.MOUSEBUTTONDOWN and main_board.turn == my_id and not main_board.check_winner():
                    pos = pygame.mouse.get_pos()
                    coords = main_board.get_clicked_pos(pos)
                    if coords:
                        old_selected = main_board.selected_piece
                        main_board.select_piece(coords[0], coords[1])

                        # SPRAWDZAMY CZY RUCH SIĘ ODBYŁ:
                        if old_selected and old_selected != (coords[0], coords[1]):
                            move_data = f"{old_selected[0]},{old_selected[1]}:{coords[0]},{coords[1]}|"
                            net.send(move_data)

            # Obsługa przycisku Poddaj / Nowa gra
            if state in ["GAME_2P", "GAME_PC"] and btn_poddaj.is_clicked(event):
                winner = main_board.check_winner()

                if state == "GAME_PC" and main_board.turn == 2 and not winner:
                    pass
                else:
                    if winner:
                        main_board.create_starting_board()
                        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
                    else:
                        for r in range(8):
                            for c in range(8):
                                p = main_board.board_state[r][c]
                                if main_board.turn == 1 and p in [1, 10]:
                                    main_board.board_state[r][c] = 0
                                elif main_board.turn == 2 and p in [2, 20]:
                                    main_board.board_state[r][c] = 0
                        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)

            if state in ["GAME_2P", "GAME_PC"]:
                if btn_zapisz.is_clicked(event):
                    main_board.save_history_to_file()

        # --- LOGIKA POZA PĘTLĄ ZDARZEŃ ---
        if state == "GAME_PC":
            draw_game_screen(main_board)
            winner = main_board.check_winner()

            if main_board.turn == 1 or winner:
                btn_poddaj.text = "Nowa Gra" if winner else "Poddaj"
                btn_poddaj.draw(SCREEN)

            if main_board.turn == 2 and not winner:
                ai_timer += clock.get_time()
                if ai_timer > 500:
                    move = get_best_move(main_board, 2)
                    if move:
                        main_board.select_piece(move[0][0], move[0][1])
                        main_board.select_piece(move[1][0], move[1][1])
                    ai_timer = 0
        # Wykrywanie końca gry i aktualizacja statystyk
        if state in ["GAME_2P", "GAME_PC", "GAME_ONLINE"] and not game_recorded:
            winner = main_board.check_winner()
            if winner:
                stats["games_played"] += 1
                stats["kings_created"] += main_board.kings_this_game

                if state == "GAME_2P":
                    if winner == 1:
                        stats["mode_2p"]["wins"] += 1
                    else:
                        # W trybie 2P 'losses' oznacza wygraną gracza 2
                        stats["mode_2p"]["losses"] += 1

                elif state == "GAME_PC":
                    if winner == 1:
                        stats["mode_pc"]["wins"] += 1
                    else:
                        stats["mode_pc"]["losses"] += 1

                elif state == "GAME_ONLINE":
                    # Zakładamy, że my_id to nasze ID gracza.
                    if winner == my_id:
                        stats["mode_online"]["wins"] += 1
                    else:
                        stats["mode_online"]["losses"] += 1

                save_stats(stats)
                game_recorded = True

                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)

        # Rysowanie interfejsu w zależności od stanu
        if state == "STATS":
            draw_stats(stats)
        elif state == "MENU":
            draw_menu()
            if os.path.exists(SAVE_FILE):
                pass
        elif state == "SETTINGS":
            draw_settings()
        elif state in ["GAME_2P", "GAME_PC"]:
            draw_game_screen(main_board)
            winner = main_board.check_winner()
            btn_poddaj.text = "Nowa Gra" if winner else "Poddaj"
            btn_poddaj.draw(SCREEN)
            btn_zapisz.draw(SCREEN)
        elif state == "GAME_PC":
            draw_game_screen(main_board)
            winner = main_board.check_winner()
            btn_poddaj.text = "Nowa Gra" if winner else "Poddaj"
            btn_poddaj.draw(SCREEN)
            # Logika ruchu sztucznej inteligencji
            if main_board.turn == 2 and not winner:
                ai_timer += clock.get_time()
                if ai_timer > 500:
                    if main_board.must_continue_jump:
                        moves = main_board.valid_moves
                        if moves:
                            end_pos = list(moves.keys())[0]
                            main_board.select_piece(end_pos[0], end_pos[1])
                    else:
                        move = get_best_move(main_board, 2)
                        if move:
                            start_pos, end_pos = move
                            main_board.select_piece(start_pos[0], start_pos[1])
                            main_board.select_piece(end_pos[0], end_pos[1])
                    ai_timer = 0

        elif state == "GAME_ONLINE":
            draw_game_screen(main_board)
            # Sprawdzanie czy przyszedł ruch od przeciwnika
            raw_data = net.receive()
            if raw_data:
                moves = raw_data.split("|")
                for move in moves:
                    if not move or ":" not in move:
                        continue
                    try:
                        start_str, end_str = move.split(":")
                        s_r, s_c = map(int, start_str.split(","))
                        e_r, e_c = map(int, end_str.split(","))
                        main_board.select_piece(s_r, s_c)
                        main_board.select_piece(e_r, e_c)
                    except Exception as e:
                        print(f"Błąd synchronizacji ruchu: {e}")

        pygame.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    main()