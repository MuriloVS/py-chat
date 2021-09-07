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
            # e chama a função para repassar a todos os clientes
            broadcast(message)
        except:
            # removendo o cliente das listas
            index = clients.index(client)
            clients.pop(index)
            nick = nicknames.pop(index)
            # e finalizando a conexão
            client.close()
            broadcast(f'{nick} se desconectou!\n'.encode('utf-8'))
            break


def receive(server):
    while True:
        # accept inicia a conexão com o servidor, retornando dados
        # do cliente e endereço/porta usados
        client, address = server.accept()
        clients.append(client)

        # mensagem repassada ao cliente utilizando o socket dele
        # para solicitar o nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        print(f'{nickname} se conectou em {address}')
        broadcast(f'{nickname} se conectou!\n'.encode('utf-8'))

        # feita a conexão com o cliente iniciamos uma thread para
        # lidar com esta conexão
        thread = threading.Thread(target=client_handler, args=(client, ))
        thread.start()


def create_server():
    # AF_INET se recere ao IPV4 e o SOCK_STREAM ao protocolo TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # o bind víncula o servidor ao endereço e porta fornecidos
    server.bind((LOCALHOST, PORT))
    # listen para esperar as conexões - limitadas a 15
    # no caso de uma hipotética 16ª conexão esta seria rejeitada
    server.listen(15)
    print(f'Servidor rodando em {LOCALHOST} na porta {PORT}')
    return server


if __name__ == '__main__':
    # cria o servidor
    server = create_server()
    # e espera as conexões
    receive(server)
