from constants import *


# --- KLASA PLANSZY GRY ---
from constants import *


class GameBoard:
    def __init__(self, screen_width, screen_height):
        self.rows = 8
        self.cols = 8
        self.square_size = min(screen_width, screen_height) // 10
        self.board_width = self.cols * self.square_size
        self.board_height = self.rows * self.square_size
        self.start_x = (screen_width - self.board_width) // 2
        self.start_y = (screen_height - self.board_height) // 2 + 20

        # --- LOGIKA ---
        self.board_state = []
        self.turn = 1  # 1 dla Gracza 1 (Czerwone), 2 dla Gracza 2 (Białe)
        self.selected_piece = None  # Przechowuje (row, col) wybranego pionka
        self.valid_moves = {}  # Słownik dostępnych ruchów dla wybranego pionka
        self.must_continue_jump = False
        self.create_starting_board()

    def create_starting_board(self):
        """Tworzy macierz 8x8. 0=puste, 1=czerwony, 2=biały, 10=czerwona damka, 20=biała damka."""
        self.board_state = []
        for row in range(self.rows):
            self.board_state.append([])
            for col in range(self.cols):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board_state[row].append(2)
                    elif row > 4:
                        self.board_state[row].append(1)
                    else:
                        self.board_state[row].append(0)
                else:
                    self.board_state[row].append(0)
        self.turn = 1
        self.selected_piece = None
        self.must_continue_jump = False

    def get_clicked_pos(self, pos):
        """Zamienia piksele myszki na (row, col) planszy."""
        x, y = pos
        row = (y - self.start_y) // self.square_size
        col = (x - self.start_x) // self.square_size
        if 0 <= row < 8 and 0 <= col < 8:
            return int(row), int(col)
        return None

    def draw(self, surface):
        # Rysowanie pól
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * self.square_size
                y = self.start_y + row * self.square_size
                color = BOARD_DARK if col % 2 == ((row + 1) % 2) else BOARD_LIGHT

                if self.selected_piece == (row, col):
                    color = (100, 200, 100)  # Zielony dla zaznaczonego
                pygame.draw.rect(surface, color, (x, y, self.square_size, self.square_size))

                # Rysowanie kropek podpowiedzi
                if (row, col) in self.valid_moves:
                    center_x = x + self.square_size // 2
                    center_y = y + self.square_size // 2
                    pygame.draw.circle(surface, (0, 255, 0), (center_x, center_y), 10)

        # Rysowanie pionków
        radius = self.square_size // 2 - 8
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board_state[row][col]
                if piece != 0:
                    center_x = self.start_x + col * self.square_size + self.square_size // 2
                    center_y = self.start_y + row * self.square_size + self.square_size // 2

                    piece_color = PIECE_PLAYER_1 if piece in [1, 10] else PIECE_PLAYER_2
                    pygame.draw.circle(surface, piece_color, (center_x, center_y), radius)
                    pygame.draw.circle(surface, PIECE_BORDER, (center_x, center_y), radius, 3)

                    # Oznaczenie damki
                    if piece >= 10:
                        pygame.draw.circle(surface, (212, 175, 55), (center_x, center_y), radius - 12, 5)

    def get_all_valid_moves(self, player_id):
        all_moves = {}
        any_capture = False

        for r in range(self.rows):
            for c in range(8):
                p = self.board_state[r][c]
                if (player_id == 1 and p in [1, 10]) or (player_id == 2 and p in [2, 20]):
                    moves = self.get_valid_moves(r, c)
                    if moves:
                        if any(len(v) > 0 for v in moves.values()):
                            any_capture = True
                        all_moves[(r, c)] = moves

        if any_capture:
            filtered = {}
            for start, moves in all_moves.items():
                only_caps = {target: cap for target, cap in moves.items() if len(cap) > 0}
                if only_caps:
                    filtered[start] = only_caps
            return filtered
        return all_moves

    def get_valid_moves(self, row, col):
        """Logika ruchów z uwzględnieniem latającej damy."""
        moves = {}
        piece = self.board_state[row][col]
        if piece == 0: return moves

        is_king = piece >= 10
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Dla zwykłych pionków ograniczamy kierunki
        if not is_king:
            allowed_dir = [(-1, -1), (-1, 1)] if piece == 1 else [(1, -1), (1, 1)]
        else:
            allowed_dir = directions

        for dr, dc in directions:
            # LOGIKA DAMY
            if is_king:
                enemy_found = False
                for i in range(1, 8):
                    nr, nc = row + dr * i, col + dc * i
                    if not (0 <= nr < 8 and 0 <= nc < 8): break

                    target = self.board_state[nr][nc]
                    if target == 0:
                        if not enemy_found:
                            moves[(nr, nc)] = []
                        else:
                            moves[(nr, nc)] = [enemy_pos]
                    elif (piece in [10] and target in [2, 20]) or (piece in [20] and target in [1, 10]):
                        if enemy_found: break
                        enemy_found = True
                        enemy_pos = (nr, nc)
                        jr, jc = nr + dr, nc + dc
                        if not (0 <= jr < 8 and 0 <= jc < 8) or self.board_state[jr][jc] != 0:
                            break
                    else:
                        break

            # LOGIKA ZWYKŁEGO PIONKA
            else:
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board_state[nr][nc]

                    # ZWYKŁY RUCH: Tylko do przodu (allowed_dir)
                    if target == 0 and (dr, dc) in allowed_dir:
                                moves[(nr, nc)] = []

                    # BICIE: W dowolną stronę
                    elif target != 0:
                        is_enemy = (piece == 1 and target in [2, 20]) or (piece == 2 and target in [1, 10])
                        if is_enemy:
                            jr, jc = nr + dr, nc + dc
                            if 0 <= jr < 8 and 0 <= jc < 8 and self.board_state[jr][jc] == 0:
                                moves[(jr, jc)] = [(nr, nc)]
        return moves

    def select_piece(self, row, col):
        legal_starts = self.get_all_valid_moves(self.turn)

        is_mid_jump = self.must_continue_jump

        if self.selected_piece and (row, col) in self.valid_moves:
            old_r, old_c = self.selected_piece
            captured = self.valid_moves[(row, col)]
            piece_val = self.board_state[old_r][old_c]

            self.board_state[row][col] = piece_val
            self.board_state[old_r][old_c] = 0
            for cr, cc in captured:
                self.board_state[cr][cc] = 0

            if captured:
                next_m = self.get_valid_moves(row, col)
                only_jumps = {k: v for k, v in next_m.items() if len(v) > 0}
                if only_jumps:
                    self.selected_piece = (row, col)
                    self.valid_moves = only_jumps
                    self.must_continue_jump = True
                    return

            if row == 0 and piece_val == 1: self.board_state[row][col] = 10
            if row == 7 and piece_val == 2: self.board_state[row][col] = 20

            self.selected_piece = None
            self.valid_moves = {}
            self.must_continue_jump = False
            self.turn = 2 if self.turn == 1 else 1
            return

        if not is_mid_jump:
            if (row, col) in legal_starts:
                self.selected_piece = (row, col)
                self.valid_moves = legal_starts[(row, col)]
            else:
                self.selected_piece = None
                self.valid_moves = {}


    def check_winner(self):
        p1 = any(p in [1, 10] for row in self.board_state for p in row)
        p2 = any(p in [2, 20] for row in self.board_state for p in row)
        if not p1: return 2
        if not p2: return 1

        # Brak ruchów = przegrana
        if not self.get_all_valid_moves(self.turn):
            return 2 if self.turn == 1 else 1

        return None