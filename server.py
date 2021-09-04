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
            message = client.rcv(1024)
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


def receive():
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((LOCALHOST, PORT))
        server.listen()

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

        thread = threading.Thread(target=client_handler, args=(client, ))
        thread.start()


def main():
    receive()


if __name__ == '__main__':
    main()
