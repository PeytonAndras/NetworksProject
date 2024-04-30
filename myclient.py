import socket
import threading
import ssl
import time
import tkinter as tk
from typing import NamedTuple
from tkinter import font
from tkinter import messagebox, font
from tictactoe_game import Move, TicTacToeGame, Player

class TicTacToeBoard(tk.Tk):
    def __init__(self, server_address, server_port):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self.winner_combo = []
        self._current_moves = [[None for _ in range(3)] for _ in range(3)]
        self.server_address = server_address
        self.server_port = server_port
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('tictactoe.crt')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wrapped_socket = self.context.wrap_socket(self.client_socket, server_hostname='localhost')
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


                if data.startswith("PLAYER") and self.player_label == None:
                    self.player_label = data.split()[1]
                    self.after(0, lambda: self.status_label.config(text=f"You are Player {self.player_label}"))

                    if self.player_label == "1":
                        self.after(0, self.enable_board)

                elif data.startswith("MOVE"):
                    _, row, col, label = data.split()
                    self.after(0, lambda: self.update_board(int(row), int(col), label))
                    
                elif data.startswith("OPPONENT_DISCONNECTED"):
                    self.reset_game()
                    self.status_label.config(text="Reset Game!")

                    if label != self.player_label:
                        self.after(0, self.enable_board)

                if data.startswith("WIN"):
                    self.reset_game()
                    self.status_label.config(text="WINNER WINNER CHICKEN DINNER")
                
                if data.startswith("TIE"):
                    self.reset_game()
                    self.status_label.config(text="Tie!")

                if data.startswith("PLAYER 1 TURN"):
                    self.status_label.config(text="Player 1's Turn")
                
                if data.startswith("PLAYER 2 TURN"):
                    self.status_label.config(text="Player 2's Turn")

            except ConnectionError:
                self.after(0, lambda: messagebox.showerror("Connection Error", "Lost connection to the server."))
                self.attempt_reconnect()
                break
    
    def attempt_reconnect(self):
        attempts = 5
        for attempt in range(attempts):
            try:
                self.after(0, lambda: self.status_label.config(text=f"Reconnecting... ({attempt + 1}/{attempts})"))
                time.sleep(2) 
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.wrapped_socket = self.context.wrap_socket(self.client_socket, server_hostname='localhost')
                self.wrapped_socket.connect((self.server_address, self.server_port))
                self.after(0, lambda: self.status_label.config(text="Reconnected!"))
                threading.Thread(target=self.listen_to_server, daemon=True).start()
                self.after(0, self.enable_board)
                return 
            except Exception as e:
                print(f"Reconnection attempt {attempt + 1} failed: {e}")

        self.after(0, lambda: self.status_label.config(text="Failed to reconnect. Please restart the application."))
        self.disable_board()

    def update_board(self, row, col, label):
        self._current_moves[row][col] = label
        button = self.cells[(row, col)]
        button.config(text=label, state='disabled')
        if label == self.player_label:
            self.status_label.config(text="Your turn")
        else:
            self.enable_board()

    def get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def reset_game(self):
        self._current_moves = [['' for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.cells[(row, col)].config(text='', state='normal')
        self.status_label.config(text="Game reset. Waiting for moves.")
def main():
    server_address = '3.144.106.235'  #3.144.106.235
    server_port = 5555
    app = TicTacToeBoard(server_address, server_port)
    app.mainloop()

if __name__ == "__main__":
    main()