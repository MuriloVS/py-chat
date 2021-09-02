import threading
import socket

LOCALHOST = '127.0.0.1'
PORT = 6789


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOCALHOST, PORT))
    server.listen()


if __name__ == main:
    main()
