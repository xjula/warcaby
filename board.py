from constants import *


# --- KLASA PLANSZY GRY ---
class GameBoard:
    def __init__(self, screen_width, screen_height):
        self.rows = 8
        self.cols = 8

        # Dynamiczny rozmiar pola (z marginesem)
        self.square_size = min(screen_width, screen_height) // 10

        self.board_width = self.cols * self.square_size
        self.board_height = self.rows * self.square_size

        # Centrowanie planszy na nowym, dowolnym ekranie
        self.start_x = (screen_width - self.board_width) // 2
        self.start_y = (screen_height - self.board_height) // 2 + 20

        self.board_state = []
        self.create_starting_board()

    def create_starting_board(self):
        self.board_state = []
        for row in range(self.rows):
            self.board_state.append([])
            for col in range(self.cols):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board_state[row].append(2)  # Czarne
                    elif row > 4:
                        self.board_state[row].append(1)  # Białe
                    else:
                        self.board_state[row].append(0)
                else:
                    self.board_state[row].append(0)

    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * self.square_size
                y = self.start_y + row * self.square_size
                color = BOARD_DARK if col % 2 == ((row + 1) % 2) else BOARD_LIGHT
                pygame.draw.rect(surface, color, (x, y, self.square_size, self.square_size))

        radius = self.square_size // 2 - 8
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board_state[row][col]
                if piece != 0:
                    center_x = self.start_x + col * self.square_size + self.square_size // 2
                    center_y = self.start_y + row * self.square_size + self.square_size // 2

                    if piece == 1:
                        piece_color = PIECE_PLAYER_1
                    else:
                        piece_color = PIECE_PLAYER_2

                        # Rysowany jest główny kolor pionka, a potem ciemna obwódka
                    pygame.draw.circle(surface, piece_color, (center_x, center_y), radius)
                    pygame.draw.circle(surface, PIECE_BORDER, (center_x, center_y), radius, 3)
                    # Wewnętrzne ozdobne kółko
                    pygame.draw.circle(surface, PIECE_BORDER, (center_x, center_y), radius - 8, 1)