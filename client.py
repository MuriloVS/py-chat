import threading
import socket
import tkinter
from tkinter.constants import DISABLED, NORMAL
import tkinter.simpledialog
import tkinter.scrolledtext
import os


LOCALHOST = '127.0.0.1'
PORT = 6789
CWD = os.getcwd()


class Client():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.nick_popup = tkinter.Tk()
        self.nick_popup.withdraw()
        self.nickname = tkinter.simpledialog.askstring(
            'Nickname', 'Escolha o seu apelido', parent=self.nick_popup)

        self.running = True
        self.interface = False

        self.window_thread = threading.Thread(target=self.window_loop)
        self.window_thread.start()
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def window_loop(self):
        self.main_window = tkinter.Tk()
        self.main_window.title('Server-Client Chat')
        self.main_window.iconbitmap(os.path.join(CWD, 'chat.ico'))
        self.main_window.configure(bg='#D3D3D3')

        self.chat_label = tkinter.Label(
            self.main_window, text='Chat', bg='#D3D3D3')
        self.chat_label.config(font=('Arial', 14))
        self.chat_label.grid(row=0, column=0, padx=2, pady=2)

        self.chat = tkinter.scrolledtext.ScrolledText(self.main_window)
        self.chat.grid(row=1, column=0, padx=10, pady=7, columnspan=2)
        # evita que o chat seja alterado diretamente
        self.chat.config(state='disabled')

        self.input_label = tkinter.Label(self.main_window, text='Mensagem')
        self.input = tkinter.Text(self.main_window, height=3)
        self.input.grid(row=2, column=0, padx=7, pady=7)

        self.send_button = tkinter.Button(
            self.main_window, text='Enviar', command=self.send)
        self.send_button.config(font=('Arial', 12))
        self.send_button.grid(row=2, column=1, padx=7, pady=7)

        self.interface = True

        self.main_window.protocol('WM_DELETE_WINDOW', self.close)
        self.main_window.mainloop()

    def receive(self):
        while self.running:
            try:
                self.server_message = self.socket.recv(1024).decode('utf-8')

                if self.server_message == 'NICK':
                    self.socket.send(self.nickname.encode('utf-8'))
                elif self.interface:
                    self.chat.config(state='normal')

                    self.chat.insert('end', self.server_message)
                    self.chat.yview('end')  # scrol down

                    self.chat.config(state='disabled')
            except:
                self.close()

    def send(self):
        # ("1.0", "end") -> do início ao fim
        self.user_input = self.input.get('1.0', 'end').strip()

        if len(self.user_input) > 0:
            self.user_message = f'{self.nickname}: {self.user_input}\n'
            self.socket.send(self.user_message.encode('utf-8'))
            # limpando o input após o envio da mensagem
            self.input.delete("1.0", "end")

    def close(self):
        self.running = False
        self.main_window.destroy()
        self.socket.close()
        exit(0)


if __name__ == '__main__':
    client = Client(LOCALHOST, PORT)
