import threading
import socket
import random


LOCALHOST = '127.0.0.1'
PORT = 6789

clients = []
nicknames = []
colors = []
sep = '--||--'


def broadcast(message):
    for client in clients:
        client.send(message)


def client_handler(client, color):
    # criando uma string com um separador e a cor
    color = sep + color
    color = bytes(color, encoding='utf-8')

    while True:
        try:
            # recebe a mensagem enviada por um cliente
            message = client.recv(1024)
            msg = str(message.decode('utf-8'))

            if msg.startswith('/nick'):
                newnick = msg.replace('/nick', "")
                index = clients.index(client)
                msg = f'NEWNICK-{nicknames[index]} alterou o seu apelido para {newnick}!'
                print(msg)
                broadcast(msg.encode('utf-8'))
                nicknames[index] = newnick
            else:
                message = message + color
                # chama a função para repassar a todos os clientes
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


def create_color():
    # cria o hex de uma cor qualquer
    # é a cor do texto do usuário no chat
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def receive(server):
    while True:
        try:
            # accept inicia a conexão com o servidor
            # retornando dados do cliente e endereço/porta usados
            client, address = server.accept()
            clients.append(client)

            # criando a cor aleatória do usuário
            color = create_color()
            colors.append(color)

            # mensagem repassada ao cliente utilizando o socket dele
            # para solicitar o nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            print(f'{nickname} se conectou em {address}')
            broadcast(f'{nickname} se conectou!\n'.encode('utf-8'))

            # feita a conexão com o cliente iniciamos uma thread para
            # lidar com esta conexão
            thread = threading.Thread(
                target=client_handler, args=(client, color))
            thread.start()
        except:
            exit(0)


def create_server():
    # AF_INET se refere ao IPV4 e o SOCK_STREAM ao protocolo TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # o bind vincula o servidor ao endereço e porta fornecidos
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
