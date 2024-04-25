from typing import NamedTuple, List

class Player(NamedTuple):
    label: str
    conn: any  # Connection object for the player

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

BOARD_SIZE = 3

class TicTacToeGame:
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.players = []  # This will hold Player objects which include the connection
        self.current_moves = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_player_index = 0
        self.has_winner = False
        self.winner_combo = []

    def add_player(self, conn):
        if len(self.players) < 2:
            player_label = "X" if len(self.players) == 0 else "O"
            player = Player(label=player_label, conn=conn)
            self.players.append(player)
            return len(self.players) - 1  # Return player ID
        return None  # No more players can be added

    def process_move(self, move, player_id):
        """Process a move. Returns a tuple (bool, str) indicating whether the move was valid, and the game status ("", "WIN", "TIE")."""
        if self.has_winner or self.current_player_index != player_id:
            return False, ""
        row, col = move.row, move.col
        if self.current_moves[row][col] is not None:
            return False, ""  # Invalid move
        self.current_moves[row][col] = move.label
        if self.check_winner():
            self.has_winner = True
            return True, "WIN"
        if self.check_tie():
            return True, "TIE"
        self.toggle_player()
        return True, ""

    def check_winner(self):
        # Check rows, columns, and diagonals for a win
        lines = self.current_moves + list(map(list, zip(*self.current_moves)))  # Rows and columns
        lines.append([self.current_moves[i][i] for i in range(self.board_size)])  # Diagonal
        lines.append([self.current_moves[i][self.board_size-i-1] for i in range(self.board_size)])  # Anti-diagonal
        for line in lines:
            if len(set(line)) == 1 and line[0] is not None:
                return True
        return False

    def check_tie(self):
        return all(all(cell is not None for cell in row) for row in self.current_moves)

    def toggle_player(self):
        self.current_player_index = (self.current_player_index + 1) % 2

    def reset_game(self):
        self.current_moves = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player_index = 0
        self.has_winner = False
        self.winner_combo = []