import socket
import threading
import ssl
import time
import tkinter as tk
from typing import NamedTuple
from tkinter import font
from tkinter import messagebox, font
from tictactoe_game import Move, TicTacToeGame, Player

#class to represent the Tic-Tac-Toe board
class TicTacToeBoard(tk.Tk):
    def __init__(self, server_address, server_port):
        super().__init__()
        #self.game_logic = tic_tac_toe.TicTacToeGame.get_winning_combos()
        self.title("Tic-Tac-Toe Game")
        self.winner_combo = []
        self._current_moves = [[None for _ in range(3)] for _ in range(3)]
        self.server_address = server_address
        self.server_port = server_port
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('tictactoe.crt')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.connect(server_address, server_port)
        self.wrapped_socket = self.context.wrap_socket(self.client_socket, server_hostname='localhost')
        self.wrapped_socket.connect((self.server_address, self.server_port))
        self.player_label = None
        self.create_widgets()
        self.disable_board()
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    #function to create the game board
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

    #function to disable the board
    def disable_board(self):
        for button in self.cells.values():
            button.config(state='disabled')

    #function to enable the board
    def enable_board(self):
        for button in self.cells.values():
            button.config(state='normal')

    #function to send the move to the server
    def send_move_to_server(self, row, col):
        self.disable_board()
        self.wrapped_socket.sendall(f"{row}:{col}".encode())

    #function to listen to the server
    def listen_to_server(self):
        while True:
            try:
                data = self.wrapped_socket.recv(1024).decode()
                if not data:
                    continue

                #handle PLAYER message to assign player number to this client
                if data.startswith("PLAYER") and self.player_label == None:
                    self.player_label = data.split()[1]
                    #update connection status immediately upon receiving player assignment
                    self.after(0, lambda: self.status_label.config(text=f"You are Player {self.player_label}"))

                    #if this client is Player 1, enable the board to start the game
                    if self.player_label == "1":
                        self.after(0, self.enable_board)
                #handle MOVE message to update the board with the opponent's move
                elif data.startswith("MOVE"):
                    _, row, col, label = data.split()
                    self.after(0, lambda: self.update_board(int(row), int(col), label))
                    
                elif data.startswith("OPPONENT_DISCONNECTED"):
                    self.reset_game()
                    self.status_label.config(text="Reset Game!")

                    #enable the board if it's this client's turn next; this logic might need refinement based on server's game state management
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

                #handle WIN, TIE, and INVALID MOVE messages as previously described
            #handle ConnectionError to notify the user of the lost connection
            except ConnectionError:
                self.after(0, lambda: messagebox.showerror("Connection Error", "Lost connection to the server."))
                self.attempt_reconnect()
                break
    
    #function to attempt reconnection
    def attempt_reconnect(self):
        attempts = 5
        for attempt in range(attempts):
            try:
                self.after(0, lambda: self.status_label.config(text=f"Reconnecting... ({attempt + 1}/{attempts})"))
                time.sleep(2)  # Wait a bit before trying to reconnect
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.wrapped_socket = self.context.wrap_socket(self.client_socket, server_hostname='localhost')
                self.wrapped_socket.connect((self.server_address, self.server_port))
                self.after(0, lambda: self.status_label.config(text="Reconnected!"))
                threading.Thread(target=self.listen_to_server, daemon=True).start()
                self.after(0, self.enable_board)
                return  # Exit the function upon successful reconnection
            except Exception as e:
                print(f"Reconnection attempt {attempt + 1} failed: {e}")

        self.after(0, lambda: self.status_label.config(text="Failed to reconnect. Please restart the application."))
        self.disable_board()

    #function to update the board with the opponent's move
    def update_board(self, row, col, label):
        self._current_moves[row][col] = label  # Update the internal state
        button = self.cells[(row, col)]
        button.config(text=label, state='disabled')
        if label == self.player_label:
            self.status_label.config(text="Your turn")
        else:
            self.enable_board()

    #function to handle the window close event
    def get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]
    
    #function to handle the window close event
    def reset_game(self):
        """Reset the game."""
        self._current_moves = [['' for _ in range(3)] for _ in range(3)]  # Reset the current moves
        for row in range(3):
            for col in range(3):
                self.cells[(row, col)].config(text='', state='normal')  # Clear text and enable button
        self.status_label.config(text="Game reset. Waiting for moves.")
def main():
    server_address = '3.144.106.235'  #3.144.106.235
    server_port = 5555
    app = TicTacToeBoard(server_address, server_port)
    app.mainloop()

if __name__ == "__main__":
    main()