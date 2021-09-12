import threading
import socket
import tkinter
from tkinter.constants import DISABLED, NORMAL
import tkinter.simpledialog
import tkinter.scrolledtext
import datetime
import random
import os
import gc


LOCALHOST = '127.0.0.1'
PORT = 6789
sep = '--||--'
CWD = os.getcwd()


class Client():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        # pequeno popup para que o usuário digite o seu apelido
        self.nick_popup = tkinter.Tk()
        self.nick_popup.withdraw()
        temp = 'user_' + str(random.randint(0, 999999999))
        self.nickname = tkinter.simpledialog.askstring(
            title='Apelido', prompt='Escolha o seu apelido', initialvalue=temp, parent=self.nick_popup)

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

        # configurações para melhorar a responsividade da janela
        tkinter.Grid.columnconfigure(self.main_window, index=0, weight=0)
        tkinter.Grid.columnconfigure(self.main_window, index=1, weight=1)
        tkinter.Grid.rowconfigure(self.main_window, index=0, weight=0)
        tkinter.Grid.rowconfigure(self.main_window, index=1, weight=1)
        tkinter.Grid.rowconfigure(self.main_window, index=2, weight=0)

        # título acima do histórico de mensagens
        self.chat_label = tkinter.Label(
            self.main_window, text='Sala de bate-papo', bg='#D3D3D3')
        self.chat_label.config(font=('Arial', 14))
        self.chat_label.grid(row=0, column=0, columnspan=2,
                             padx=10, pady=2, sticky='w')

        # áre com o histórico de mensagens
        self.chat = tkinter.scrolledtext.ScrolledText(self.main_window)
        self.chat.grid(row=1, column=1, padx=10, pady=7,
                       columnspan=2, sticky='nsew')
        # self.chat.grid_columnconfigure(0, weight=1)
        # evita que o chat seja alterado diretamente
        self.chat.config(state='disabled', width=60)

        # local onde o usuário pode digitar o seu texto
        self.input = tkinter.Text(self.main_window, height=1)
        self.input.grid(row=2, column=1,
                        padx=10, pady=8, sticky='nwe')
        # self.input.grid_columnconfigure(0, weight=1)
        self.input.config(width=52)
        self.input.focus_set()
        # víncula a tecla 'enter/return' à função de envio de msg
        self.input.bind('<Return>', lambda _: self.send())

        # botão para envio de mensagens
        self.send_button = tkinter.Button(
            self.main_window, text='Enviar', command=self.send)
        self.send_button.config(font=('Arial', 12))
        self.send_button.grid(row=2, column=2, padx=7, pady=7, sticky='e')

        self.interface = True

        # protoclo de fechamento vinculado a um método chamado close
        self.main_window.protocol('WM_DELETE_WINDOW', self.close)
        # mainloop() executa a janela até algum evento (user fechar o programa)
        self.main_window.mainloop()

    def receive(self):
        while self.running:
            try:
                # recebe as mensagens do servidor
                self.server_message = self.socket.recv(1024)
                # se for a flag 'NICK' devolve o apelido do usuário ao servidor
                if self.server_message.decode('utf-8') == 'NICK':
                    self.socket.send(self.nickname.encode('utf-8'))
                # interface pronta
                elif self.interface:
                    # mensagem quando o usuário se conectar
                    if self.server_message.decode('utf-8').endswith(' se conectou!\n'):
                        self.chat.config(state='normal')
                        self.chat.insert('end', self.server_message)
                        self.chat.yview('end')
                        self.chat.config(state='disabled')
                    # mensagem quando o usuário se desconectar
                    elif self.server_message.decode('utf-8').endswith(' se desconectou!\n'):
                        self.chat.config(state='normal')
                        self.chat.insert('end', self.server_message)
                        self.chat.yview('end')
                        self.chat.config(state='disabled')
                    # mensagem quando o usuário mudar o apelido
                    elif self.server_message.decode('utf-8').startswith('NEWNICK-'):
                        self.server_message = self.server_message.decode(
                            'utf-8').replace('NEWNICK-', "")
                        self.chat.config(state='normal')
                        self.chat.insert('end', self.server_message + '\n')
                        self.chat.yview('end')
                        self.chat.config(state='disabled')
                    # mensagens normais de conversa entre os usuários
                    else:
                        msg_color = self.server_message.decode(
                            'utf-8').split(sep)
                        self.server_message = msg_color[0]
                        self.color = msg_color[1]
                        # libera a escrita no widget de scrolltext
                        self.chat.config(state='normal')
                        # o terceiro parâmetro é uma tag para identificar a mensagem
                        self.chat.insert(
                            'end', self.server_message, self.color)
                        # aqui pegamos a mensagem com a tag já definida e alteramos a cor
                        self.chat.tag_config(self.color, foreground=self.color)
                        # scroll down - mensagens inseridas rolam a tela para baixo
                        self.chat.yview('end')
                        # e trava novamente a escrita no scrolltext
                        self.chat.config(state='disabled')
            except:
                break

    def send(self):
        # ("1.0", "end") -> do início ao fim
        self.user_input = self.input.get('1.0', 'end').strip()
        # se clicar enviar ou enter sem input nada é enviado
        if len(self.user_input) > 0:
            # trocando o nick do usuário
            if self.user_input.startswith('/nick '):
                newnick = self.user_input.split(' ', 1)
                self.nickname = newnick[1]
                self.main_window.title(f'Chat Client do {self.nickname}')
                # newnick[0] = '/nick' e newnick[1] = o novo nick do user
                self.socket.send((newnick[0]+newnick[1]).encode('utf-8'))
            else:
                # msg normal de chat
                now = datetime.datetime.now()
                now = now.strftime("%d/%m/%y %H:%M:%S")
                self.user_message = f'{now} {self.nickname}: {self.user_input}\n'
                self.socket.send(self.user_message.encode('utf-8'))

            # limpando o input após a entrada do usuário
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
