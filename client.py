from server import receive
import threading
import socket
import tkinter
from tkinter.constants import DISABLED, NORMAL
import tkinter.simpledialog
import tkinter.scrolledtext
import os
import gc


LOCALHOST = '127.0.0.1'
PORT = 6789
CWD = os.getcwd()


class Client():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        # pequeno popup para que o usuário digite o seu apelido
        self.nick_popup = tkinter.Tk()
        self.nick_popup.withdraw()
        self.nickname = tkinter.simpledialog.askstring(
            'Apelido', 'Escolha o seu apelido', parent=self.nick_popup)

        # variáveis para controlar a exeução do programa e a GUI
        self.running = True
        self.interface = False

        # uma thread para a GUI (que também cuida do envio de mensagens)
        # e outra para receber mensagens do servidor
        self.window_thread = threading.Thread(target=self.window_loop)
        self.window_thread.start()
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def window_loop(self):
        # criando a tela principal
        self.main_window = tkinter.Tk()
        self.main_window.title(f'Chat Client do {self.nickname}')
        self.main_window.iconbitmap(os.path.join(CWD, 'chat.ico'))
        self.main_window.configure(bg='#D3D3D3')

        # título acima do histórico de mensagens
        self.chat_label = tkinter.Label(
            self.main_window, text='Chat Multiusuário', bg='#D3D3D3')
        self.chat_label.config(font=('Arial', 14))
        self.chat_label.grid(row=0, column=0, padx=2, pady=2)

        # áre com o histórico de mensagens
        self.chat = tkinter.scrolledtext.ScrolledText(self.main_window)
        self.chat.grid(row=1, column=0, padx=10, pady=7, columnspan=2)
        # evita que o chat seja alterado diretamente
        self.chat.config(state='disabled', width=60)

        # local onde o usuário pode digitar o seu texto
        self.input = tkinter.Text(self.main_window, height=1)
        self.input.grid(row=2, column=0, padx=7, pady=7)
        self.input.config(width=52)
        self.input.focus_set()
        # víncula a tecla 'enter/return' à função de envio de msg
        self.input.bind('<Return>', lambda _: self.send())

        # botão para envio de mensagens
        self.send_button = tkinter.Button(
            self.main_window, text='Enviar', command=self.send)
        self.send_button.config(font=('Arial', 12))
        self.send_button.grid(row=2, column=1, padx=7, pady=7)

        self.interface = True

        # protoclo de fechamento vinculado a um método chamado close
        self.main_window.protocol('WM_DELETE_WINDOW', self.close)
        # mainloop() executa a janela até algum evento (user fechar o programa)
        self.main_window.mainloop()

    def receive(self):
        while self.running:
            try:
                # recebe as mensagens do servidor
                self.server_message = self.socket.recv(1024).decode('utf-8')
                # se for a flag 'NICK' devolve o apelido do usuário ao servidor
                if self.server_message == 'NICK':
                    self.socket.send(self.nickname.encode('utf-8'))
                elif self.interface:
                    # libera a escrita no widget de scrolltext
                    self.chat.config(state='normal')
                    self.chat.insert('end', self.server_message)
                    # scroll down - mensagens inseridas rolam a tela para baixo
                    self.chat.yview('end')
                    # e trava novamente a escrita no scrolltext
                    self.chat.config(state='disabled')
            except:
                break

    def send(self):
        # ("1.0", "end") -> do início ao fim
        self.user_input = self.input.get('1.0', 'end').strip()
        # se clicar enviar ou enter nada é enviado
        if len(self.user_input) > 0:
            self.user_message = f'{self.nickname}: {self.user_input}\n'
            self.socket.send(self.user_message.encode('utf-8'))
            # limpando o input após o envio da mensagem
            self.input.delete("1.0", "end")

    def close(self):
        self.running = False
        self.main_window = None
        gc.collect()
        self.socket.close()
        exit(0)


if __name__ == '__main__':
    # cria o cliente passando o IP e a porta
    client = Client(LOCALHOST, PORT)
