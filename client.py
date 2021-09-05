import threading
import socket
import tkinter
import tkinter.simpledialog
import tkinter.scrolledtext


LOCALHOST = '127.0.0.1'
PORT = 6789


class Client():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        user = tkinter.Tk()
        user.withdraw()
        self.nickname = tkinter.simpledialog.askstring(
            'Nickname', 'Escolha o seu apelido', parent=user)

        self.running = True
        self.interface = False

        window_thread = threading.Thread(target=self.window_loop)
        window_thread.start()
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def window_loop(self):
        self.main_window = tkinter.Tk()
        self.main_window.configure(bg='lightgray')

        self.chat_label = tkinter.Label(
            self.main_window, text='Chat', bg='lightgray')
        self.chat_label.config(font=('Arial', 14))
        self.chat_label.pack(padx=10, pady=5)

        self.chat = tkinter.scrolledtext.ScrolledText(self.main_window)
        self.chat.pack(padx=10, pady=5)
        # evita que o chat seja alterado diretamente
        self.chat.config(state='disabled')

        self.input_label = tkinter.Label(self.main_window, text='Mensagem')
        self.input = tkinter.Text(self.main_window, height=3)
        self.input.pack(padx=10, pady=5)

        self.send_button = tkinter.Button(
            self.main_window, text='Enviar', command=self.send)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(padx=10, pady=5)

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
                print('erro')
                self.close()

    def send(self):
        # ("1.0", "end") -> do início ao fim
        self.user_message = f'{self.nickname}: {self.input.get("1.0", "end")}'
        print(self.user_message)
        if len(self.user_message) > 0:
            print("ok")
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
