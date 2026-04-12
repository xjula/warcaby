import copy
import math

def get_best_move(board, player):
    """
    Inicjuje algorytm Minimax. Głębokość 4-5 jest optymalna.
    """
    _, move = minimax(board, 5, -math.inf, math.inf, player, True)
    return move

def simulate_move(board, start, end):
    """ Tworzy kopię planszy i wykonuje na niej ruch przy użyciu logiki GameBoard. """
    new_board = copy.deepcopy(board)
    new_board.select_piece(start[0], start[1])
    new_board.select_piece(end[0], end[1])
    return new_board

def evaluate(board):
    """
    Ocena stanu planszy: AI (Białe - 2) vs Gracz (Czerwone - 1).
    """
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board.board_state[r][c]
            if piece == 0:
                continue
            
            # --- AI (GRACZ 2 - BIAŁE) ---
            if piece == 2:
                score += 10
                score += r * 0.2
                if c == 0 or c == 7: score += 1
            elif piece == 20:
                score += 50
                
            # --- GRACZ (GRACZ 1 - CZERWONE) ---
            elif piece == 1:
                score -= 10
                score -= (7 - r) * 0.2
                if c == 0 or c == 7: score -= 1
            elif piece == 10:
                score -= 50
                
    return score

def minimax(board, depth, alpha, beta, player, maximizing):
    # Sprawdzenie zwycięstwa w symulacji
    winner = board.check_winner()
    if winner == 2: return 1000 + depth, None
    if winner == 1: return -1000 - depth, None
    
    if depth == 0:
        return evaluate(board), None

    all_moves = board.get_all_valid_moves(player)
    
    # Brak ruchów to przegrana
    if not all_moves:
        return (-1000 if maximizing else 1000), None

    best_move = None

    if maximizing:
        max_eval = -math.inf
        for start, moves in all_moves.items():
            for end, captured in moves.items():
                new_board = simulate_move(board, start, end)
                # Po ruchu AI (2) sprawdzamy odpowiedź Gracza (1)
                current_eval, _ = minimax(new_board, depth - 1, alpha, beta, 1, False)
                
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = (start, end)
                
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
        return max_eval, best_move
    
    else:
        min_eval = math.inf
        for start, moves in all_moves.items():
            for end, captured in moves.items():
                new_board = simulate_move(board, start, end)
                # Po ruchu Gracza (1) sprawdzamy odpowiedź AI (2)
                current_eval, _ = minimax(new_board, depth - 1, alpha, beta, 2, True)
                
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = (start, end)
                
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
        return min_eval, best_move