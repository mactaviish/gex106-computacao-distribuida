import socket
import threading

HOST = '172.20.75.241'
PORT = 5000

player_ready = threading.Event()
game_started = threading.Event()
game_board = [' '] * 9
current_player = 1

def handle_client(client_socket):
    global current_player

    player_number = 0

    if not game_started.is_set():
        player_number = 1
        game_started.set()
        client_socket.send(b'start1')
    else:
        player_ready.wait()
        player_number = 2
        client_socket.send(b'start2')

    while True:
        data = client_socket.recv(1024)

        if data:
            msg = data.decode()

            if msg.startswith('move '):
                move = int(msg.split(' ')[1])

                if validate_move(move) and current_player == player_number:
                    update_board(move, player_number)
                    print_board(move, player_number)
                    check_game_status(player_number, client_socket)
                    switch_turn()
                    player_ready.set()
                    player_ready.clear()
                else:
                    client_socket.send(b'invalid')
            elif msg == 'close':
                client_socket.close()
                break

    player_ready.wait()
    client_socket.send(b'close')
    client_socket.close()

def validate_move(move):
    return game_board[move] == ' '

def update_board(move, player_number):
    game_board[move] = 'X' if player_number == 1 else 'O'

def print_board(move, player_number):
    print(f'{player_number}')
    print(f'Jogador {"X" if player_number == 1 else "O"} marcou a posição {move}')
    print(f' {game_board[0]} | {game_board[1]} | {game_board[2]} ')
    print('---+---+---')
    print(f' {game_board[3]} | {game_board[4]} | {game_board[5]} ')
    print('---+---+---')
    print(f' {game_board[6]} | {game_board[7]} | {game_board[8]} ')
    print(f'')

def check_game_status(player_number, client_socket):
    if check_winner(player_number):
        client_socket.send(b'win')
    elif check_draw():
        client_socket.send(b'draw')
    else:
        client_socket.send(b'valid')

def check_winner(player_number):
    symbol = 'X' if player_number == 1 else 'O'
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    for combination in winning_combinations:
        if game_board[combination[0]] == game_board[combination[1]] == game_board[combination[2]] == symbol:
            return True

    return False

def check_draw():
    return ' ' not in game_board

def switch_turn():
    global current_player
    current_player = 2 if current_player == 1 else 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)

    print('Coordenador iniciado. Esperando jogadores...')

    while True:
        client_socket, address = server_socket.accept()
        print(f'Jogador {address} conectado.')

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()
