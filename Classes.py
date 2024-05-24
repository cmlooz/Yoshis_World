import math


class Yoshi:
    def __init__(self, color, row, col, image, SQUARE_SIZE, ROWS, COLS):
        self.color = color
        self.row = row
        self.col = col
        self.image = image
        self.SQUARE_SIZE = SQUARE_SIZE
        self.ROWS = ROWS
        self.COLS = COLS

    def draw(self, win):
        win.blit(self.image, (self.col * self.SQUARE_SIZE, self.row * self.SQUARE_SIZE))

    def possible_moves(self, green_painted, red_painted):
        moves = []
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            if 0 <= new_row < self.ROWS and 0 <= new_col < self.COLS and (new_row, new_col) not in green_painted and (
                    new_row, new_col) not in red_painted:
                moves.append((new_row, new_col))
        return moves

class MiniMax:
    def is_valid_move(self,x, y, ROWS, COLS, green_painted, red_painted):
        return 0 <= x < ROWS and 0 <= y < COLS and (x, y) not in green_painted and (x, y) not in red_painted

    def get_valid_moves(self,x, y, ROWS, COLS, green_painted, red_painted):
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        moves = []
        for dx, dy in knight_moves:
            if self.is_valid_move(x + dx, y + dy, ROWS, COLS, green_painted, red_painted):
                moves.append((x + dx, y + dy))
        return moves

    def minimax(self, green_yoshi_position, red_yoshi_position, depth, is_maximizing, alpha, beta, player, ROWS, COLS, green_painted, red_painted):
        moves = self.get_valid_moves(green_yoshi_position[0], green_yoshi_position[1], ROWS, COLS, green_painted, red_painted)

        if depth == 0 or not moves:
            return Heuristic().heuristic(green_yoshi_position, red_yoshi_position, ROWS, COLS,green_painted,red_painted,player)

        if is_maximizing:
            max_eval = float(-math.inf)
            for move in moves:
                green_painted.add(move)
                eval = self.minimax((move[0],move[1]), red_yoshi_position, depth - 1, False, alpha, beta, player, ROWS, COLS, green_painted, red_painted)
                green_painted.remove(move)
                max_eval = float(max(max_eval, eval))
                alpha = float(max(alpha, eval))
                if beta <= alpha:
                    break
            return float(max_eval)
        else:
            min_eval = float(math.inf)
            for move in moves:
                red_painted.add(move)
                eval = self.minimax((move[0],move[1]), red_yoshi_position, depth - 1, True, alpha, beta, player, ROWS, COLS, green_painted, red_painted)
                red_painted.remove(move)
                min_eval = float(min(min_eval, eval))
                beta = float(min(beta, eval))
                if beta <= alpha:
                    break
            return float(min_eval)

class Heuristic:
    def heuristic(self,green_position,red_position, ROWS, COLS,green_painted,red_painted,current_turn):
        green_possible_moves = MiniMax().get_valid_moves(green_position[0], green_position[1], ROWS, COLS, set(green_painted),
                                                     set(red_painted))
        red_possible_moves = MiniMax().get_valid_moves(red_position[0], red_position[1], ROWS, COLS, set(green_painted),
                                                     set(red_painted))
        return float((len(green_possible_moves)-len(red_possible_moves))+(len(green_painted)-len(red_painted)))
