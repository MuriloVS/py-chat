import threading
import socket

LOCALHOST = '127.0.0.1'
PORT = 6789


def main():
    clients = []
    nicknames = []

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOCALHOST, PORT))
    server.listen()

    def broadcast(message):
        for client in clients:
            client.send(message)

    def receive():
        while True:
            client, address = server.accept()
            clients.append(client)
            print(f'{client} se conectou em {address}')

            # mensagem repassada ao cliente utilizando o socket dele
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024)
            nicknames.append(nickname)
            print(f'O nickname de {client} é {nickname}.')
            client.send('Você se conectou ao servidor.'.encode('utf-8'))

            broadcast(f'{nickname} se conectou!\n'.encode('utf-8'))


if __name__ == '__main__':
    main()
