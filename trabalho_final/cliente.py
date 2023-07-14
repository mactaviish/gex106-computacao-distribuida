import socket
import threading

HOST = '172.20.75.241'
PORT = 5000

game_board = [' '] * 9

def receive_messages(client_socket):
    global game_board

    while True:
        response = client_socket.recv(1024)

        if response == b'start1':
            print('Você é o jogador O.')
            make_move(client_socket)
        elif response == b'start2':
            print('Você é o jogador X.')
            make_move(client_socket)
        elif response == b'wait':
            print('Aguardando o início do jogo...')
        elif response == b'reject':
            print('Acesso negado. O jogo já está em andamento.')
            break
        elif response == b'valid':
            print('Movimento válido. Aguarde a jogada do outro jogador.')
            make_move(client_socket)
        elif response == b'invalid':
            print('Movimento inválido. Tente novamente.')
            make_move(client_socket)
        elif response == b'win':
            print('Parabéns! Você venceu o jogo.')
            break
        elif response == b'draw':
            print('O jogo empatou.')
            break

def make_move(client_socket):
    global game_board

    while True:
        move = input('Digite um número de 0 a 8 para fazer sua jogada: ')
        if move.isdigit() and 0 <= int(move) <= 8:
            if game_board[int(move)] == ' ':
                game_board[int(move)] = 'X'
                client_socket.sendall(('move ' + move).encode())
                break
            else:
                print('A posição já está ocupada. Tente novamente.')
        else:
            print('Jogada inválida. Digite um número de 0 a 8.')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    try:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(b'access')

        thread = threading.Thread(target=receive_messages, args=(client_socket,))
        thread.start()

        while True:
            if not thread.is_alive():
                break
    finally:
        client_socket.sendall(b'close')
        client_socket.close()
