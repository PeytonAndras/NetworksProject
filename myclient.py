import socket
import threading
import ssl
import tkinter as tk
import tic_tac_toe 
from typing import NamedTuple
from tkinter import font
from tkinter import messagebox, font
from tic_tac_toe import Move

class TicTacToeBoard(tk.Tk):
    def __init__(self, server_address, server_port):
        super().__init__()
        #self.game_logic = tic_tac_toe.TicTacToeGame.get_winning_combos()
        self.title("Tic-Tac-Toe Game")
        self.winner_combo = []
        self.server_address = server_address
        self.server_port = server_port
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('tictactoe.crt')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.connect(server_address, server_port)
        self.wrapped_socket = self.context.wrap_socket(self.client_socket, server_hostname='Sam')
        self.wrapped_socket.connect((self.server_address, self.server_port))
        self.player_label = None
        self.create_widgets()
        self.disable_board()
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def create_widgets(self):
        self.cells = {}
        self.board_frame = tk.Frame(self)
        self.board_frame.pack()
        for row in range(3):
            for col in range(3):
                button = tk.Button(self.board_frame, text='', font=font.Font(size=32), width=5, height=2,
                                   command=lambda r=row, c=col: self.send_move_to_server(r, c))
                button.grid(row=row, column=col)
                self.cells[(row, col)] = button

        self.status_label = tk.Label(self, text="Connecting to server...", font=font.Font(size=20))
        self.status_label.pack(pady=20)

    def disable_board(self):
        for button in self.cells.values():
            button.config(state='disabled')

    def enable_board(self):
        for button in self.cells.values():
            button.config(state='normal')

    def send_move_to_server(self, row, col):
        self.disable_board()
        self.wrapped_socket.sendall(f"{row}:{col}".encode())

    def listen_to_server(self):
        while True:
            try:
                data = self.wrapped_socket.recv(1024).decode()
                if not data:
                    continue

                if data.startswith("PLAYER"):
                    self.player_label = data.split()[1]
                    # Update connection status immediately upon receiving player assignment
                    self.after(0, lambda: self.status_label.config(text=f"You are Player {self.player_label}"))

                    # If this client is Player 1, enable the board to start the game
                    if self.player_label == "1":
                        self.after(0, self.enable_board)

                elif data.startswith("MOVE"):
                    _, row, col, label = data.split()
                    self.after(0, lambda: self.update_board(int(row), int(col), label))

                    # Enable the board if it's this client's turn next; this logic might need refinement based on server's game state management
                    if label != self.player_label:
                        self.after(0, self.enable_board)

                # Handle WIN, TIE, and INVALID MOVE messages as previously described

            except ConnectionError:
                self.after(0, lambda: messagebox.showerror("Connection Error", "Lost connection to the server."))
                break

    def update_board(self, row, col, label):
        button = self.cells[(row, col)]
        button.config(text=label, state='disabled')
        self.status_label.config(text=f"Player {label}'s turn")
        if label != self.player_label:
            self.enable_board()
    
    def get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def reset_game(self):
        """Reset the game."""
        self.current_player_index = 0
        self._has_winner = False
        self.winner_combo = []
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
def main():
    server_address = '0.0.0.0'  
    server_port = 5555
    app = TicTacToeBoard(server_address, server_port)
    app.mainloop()

if __name__ == "__main__":
    main()