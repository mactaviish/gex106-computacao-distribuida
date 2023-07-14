import socket

HOST = '172.20.75.241'
PORT_N1 = 5000
PORT_N2 = 5001

def send_message(client_socket, message):
    client_socket.send(message.encode())

def receive_response(client_socket):
    response = client_socket.recv(1024).decode()
    print(f'\nResposta recebida:\n{response}\n')

def execute_operation(nodo_host, nodo_port, operation):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((nodo_host, nodo_port))

        send_message(client_socket, operation)
        receive_response(client_socket)

def cadastrar():
    rg = input('Digite o RG: ')
    nome = input('Digite o nome: ')
    return f'cadastrar,{rg},{nome}'

def consultar():
    rg = input('Digite o RG: ')
    return f'consultar,{rg}'

def encerrar():
    return None

def invalida():
    print('Operação inválida. Tente novamente.')
    return ''

def run_client():
    operations = {
        '1': cadastrar,
        '2': consultar,
        '3': encerrar,
    }

    while True:
        operation = input('1 - Cadastrar \n2 - Consultar \n3 - Encerrar\nDigite a operação: ')
        operation_func = operations.get(operation, invalida)
        operation_str = operation_func()
        if operation_str != '':
            execute_operation(HOST, PORT_N1, operation_str)
        else:
            continue

        if operation == '3':
            break

run_client()
