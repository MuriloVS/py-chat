import threading
import socket

LOCALHOST = '127.0.0.1'
PORT = 6789

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def client_handler(client):
    while True:
        try:
            # recebe a mensagem enviada por um cliente
            message = client.recv(1024)
            # e envia a todos os cliente conectados
            broadcast(message)
        except:
            # removendo o cliente das listas
            index = clients.index(client)
            clients.pop(index)
            nicknames.pop(index)
            # e finalizando a conexão
            client.close()
            break


def receive(server):
    while True:
        client, address = server.accept()
        clients.append(client)

        # mensagem repassada ao cliente utilizando o socket dele
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024)
        nicknames.append(nickname)
        print(f'{nickname} se conectou em {address}')

        broadcast(f'{nickname} se conectou!\n'.encode('utf-8'))
        client.send('Você se conectou ao servidor.\n'.encode('utf-8'))

        thread = threading.Thread(target=client_handler, args=(client, ))
        thread.start()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOCALHOST, PORT))
    server.listen(15)
    print(f'Servidor rodando em {LOCALHOST} na porta {PORT}')
    receive(server)
