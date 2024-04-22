import socket

def main():
    host = '18.191.52.162'
    port = 5555

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print("Connected to the server.")

        player_mark = input("Enter your mark (X or O): ").upper()
        if player_mark not in ['X', 'O']:
            print("Invalid mark. Choose either X or O.")
            return

        client_socket.send(player_mark.encode())
        print("Waiting for other player to join...")

        while True:
            response = client_socket.recv(1024).decode()
            print(response)

            if "Both players connected" in response:
                break

        while True:
            response = client_socket.recv(1024).decode()
            print(response)

            if "Your turn" in response:
                print("Current board state:") #gets suck here and doesn't print the board
                response = client_socket.recv(1024).decode()
                print(response)

                move = input("Enter your move (row:col): ")
                client_socket.send(move.encode())
    except KeyboardInterrupt:
        print("\nClient shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()