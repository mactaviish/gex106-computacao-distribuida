import socket
import threading

HOST = '172.20.75.241'
PORT = 5000
MAX_CLIENTS = 2

SIZE = 10

semaphore = threading.Semaphore()
received_messages = {}

hash_table_n1 = [None] * SIZE

def handle_client(client_socket, client_address):
    while True:
        data = client_socket.recv(1024)

        if data:
            msg = data.decode()
            print(f'Mensagem de {client_address}: {msg}')
            if msg.startswith('cadastrar'):
                _, rg, nome = msg.split(',')
                rg = int(rg.strip())
                nome = nome.strip()

                position = hash_function(rg)
                response = register_entry(position, rg, nome)
                if response.startswith('Registro cadastrado'):
                    send_response(client_socket, response)
                else:
                    response_from_n2 = forward_request_to_n2(msg)
                    send_response(client_socket, response_from_n2)
            elif msg.startswith('consultar'):
                _, rg = msg.split(',')
                rg = int(rg.strip())

                position = hash_function(rg)
                entry = get_entry(position)
                if entry and entry['rg'] == rg:
                    response = f'Registro encontrado localmente no Nodo 1:\nRG={entry["rg"]}, Nome={entry["nome"]}'
                else:
                    response = f'Registro não encontrado localmente no Nodo 1, verificando no Nodo 2...\n'
                    response_from_n2 = forward_request_to_n2(msg)
                    response += response_from_n2

                send_response(client_socket, response)

def hash_function(rg):
    return rg % SIZE

def register_entry(position, rg, nome):
    if hash_table_n1[position] is None:
        hash_table_n1[position] = {'rg': rg, 'nome': nome}
        return f'Registro cadastrado localmente no Nodo 1 na posição {position}'
    else:
        return f'Posição {position} já ocupada no Nodo 1'

def get_entry(position):
    return hash_table_n1[position]

def send_response(client_socket, response):
    semaphore.acquire()
    client_socket.send(response.encode())
    semaphore.release()

def forward_request_to_n2(operation):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, 5001))
        send_message(client_socket, operation)
        response = receive_response(client_socket)
    return response

def send_message(client_socket, message):
    client_socket.send(message.encode())

def receive_response(client_socket):
    response = client_socket.recv(1024).decode()
    return response

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CLIENTS)

    print('Coordenador do Nodo 1 iniciado. Esperando clientes...')

    while True:
        client_socket, address = server_socket.accept()
        print(f'Cliente {address} conectado.')

        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()
