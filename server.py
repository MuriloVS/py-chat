import threading
import socket
import random
import pickle


LOCALHOST = '127.0.0.1'
PORT = 6789

clients = []
nicknames = []
colors = []


def broadcast(message):
    for client in clients:
        client.send(message)


def client_handler(client):
    while True:
        try:
            # recebe a mensagem enviada por um cliente
            message = client.recv(1024)
            if message.decode('utf-8') == 'NICKNAMES':
                data = pickle.dumps(nicknames)
                client.send(data)
            elif message.decode('utf-8') == 'COLORS':
                data = pickle.dumps(colors)
                client.send(data)
            elif message.decode('utf-8') == 'DATA':
                data = pickle.dumps(dict(zip(nicknames, colors)))
                client.send(data)
            else:
                broadcast(message)
        except:
            # removendo o cliente das listas
            index = clients.index(client)
            clients.pop(index)
            colors.pop(index)
            nick = nicknames.pop(index)
            # e finalizando a conexão
            client.close()
            broadcast(f'{nick} se desconectou!\n'.encode('utf-8'))
            break


def receive(server):
    while True:
        client, address = server.accept()
        clients.append(client)

        random_number = random.randint(0, 16777215)
        hex_number = str(hex(random_number))
        hex_number = '#' + hex_number[2:]
        colors.append(hex_number)

        # mensagem repassada ao cliente utilizando o socket dele
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        print(f'{nickname} se conectou em {address}')
        broadcast(f'{nickname} se conectou!\n'.encode('utf-8'))

        thread = threading.Thread(target=client_handler, args=(client, ))
        thread.start()


def create_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOCALHOST, PORT))
    server.listen(15)
    print(f'Servidor rodando em {LOCALHOST} na porta {PORT}')
    return server


if __name__ == '__main__':
    server = create_server()
    receive(server)
