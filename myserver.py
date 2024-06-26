import socket
import threading
import ssl
from tictactoe_game import TicTacToeGame, Player, Move

def handle_client(conn, addr, game, player_id, wrapped_socket):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Received move from {addr}: {data}")
            if player_id == 0:
                broadcast("PLAYER 2 TURN", game)
            else:
                broadcast("PLAYER 1 TURN", game)
            row, col = map(int, data.split(':'))
            valid_move, game_status = game.process_move(Move(row, col, game.players[player_id].label), player_id)
            if valid_move:
                broadcast(f"MOVE {row} {col} {game.players[player_id].label}", game)
                if game_status != "":
                    print("theres a winner or a tie")
                    broadcast(game_status, game)
                    game.reset_game()
            else:
                conn.sendall("INVALID MOVE".encode())
    except Exception as e:
            print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(len(game.players))
        handle_disconnect(game, player_id, wrapped_socket)

def broadcast(message, game):
    for player in game.players:
        player.conn.sendall(message.encode())

def accept_connections(wrapped_socket, game):
    while len(game.players) < 2:
        conn, addr = wrapped_socket.accept()
        player_id = game.add_player(conn)
        print(f"Player {player_id + 1} connected from {addr}")
        conn.sendall(f"PLAYER {player_id + 1}".encode())
        threading.Thread(target=handle_client, args=(conn, addr, game, player_id, wrapped_socket)).start()

def handle_disconnect(game, player_id, wrapped_socket):
    print(len(game.players))
    print(f"Player {player_id + 1} disconnected")
    if(player_id == 0):
        game.players.pop(0)
    else: game.players.pop(1)
    broadcast("OPPONENT_DISCONNECTED", game)
    print("Player 2 wins by default")
    game.reset_game()
    accept_connections(wrapped_socket, game)


def server_main():
    host = '0.0.0.0'
    port = 5555
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="tictactoe.crt", keyfile="tictactoe.key")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wrapped_socket = context.wrap_socket(server_socket, server_side=True)
    wrapped_socket.bind((host, port))
    wrapped_socket.listen(2)
    print("Server started. Waiting for players...")

    game = TicTacToeGame()

    accept_connections(wrapped_socket, game)

if __name__ == "__main__":
    server_main()