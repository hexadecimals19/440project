import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Chat Room")

        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=20)

        self.text_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=50, height=20, state='disabled')
        self.text_area.pack()

        self.msg_entry = tk.Entry(self.frame, width=50)
        self.msg_entry.pack(pady=10)

        self.send_button = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_button.pack()

        self.quit_button = tk.Button(self.frame, text="Quit", command=self.quit_chat)
        self.quit_button.pack(pady=10)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))

        self.authenticate()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def authenticate(self):
        while True:
            username = simpledialog.askstring("Username", "Enter your username:", parent=self.master)
            password = simpledialog.askstring("Password", "Enter your password:", parent=self.master, show='*')

            self.client_socket.send(username.encode())
            self.client_socket.send(password.encode())

            response = self.client_socket.recv(1024).decode()
            if "Login successful" in response:
                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, response + '\n')
                self.text_area.config(state='disabled')
                self.text_area.see(tk.END)
                break
            else:
                messagebox.showerror("Error", response)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.text_area.config(state='normal')
                    self.text_area.insert(tk.END, message + '\n')
                    self.text_area.config(state='disabled')
                    self.text_area.see(tk.END)
                else:
                    self.client_socket.close()
                    break
            except:
                self.client_socket.close()
                break

    def send_message(self):
        message = self.msg_entry.get()
        if message:
            self.client_socket.send(message.encode())
            self.msg_entry.delete(0, tk.END)

    def quit_chat(self):
        self.client_socket.send('Client has left the chat'.encode())
        self.client_socket.close()
        self.master.quit()

def main():
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
