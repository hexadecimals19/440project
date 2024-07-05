import socket
import tkinter as tk
from tkinter import simpledialog
from cryptography.fernet import Fernet
from threading import Thread

# Client configuration
HOST = '192.168.1.177'
PORT = 8080

# Load encryption key from file
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("RTSCL V1.0")

        self.chat_log = tk.Text(master, state='disabled')
        self.chat_log.pack()

        self.message_entry = tk.Entry(master)
        self.message_entry.pack()
        self.message_entry.bind("<Return>", self.send_message)

        self.leave_button = tk.Button(master, text="Leave RTSCL", command=self.leave_chat)
        self.leave_button.pack()

        self.username = simpledialog.askstring("Username", "Enter your Username")

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.username.encode())

            auth_response = self.client_socket.recv(1024).decode()
            if auth_response != "Authentication successful":
                print("Authentication failed")
                self.master.destroy()
                return

            Thread(target=self.receive_messages).start()

            # Display welcome message in the client's own chat window
            self.display_message(f"Welcome to RTSCL, {self.username}!")

        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.master.destroy()

    def send_message(self, event):
        message = self.message_entry.get()
        encrypted_message = cipher.encrypt(message.encode())
        self.client_socket.send(encrypted_message)
        self.message_entry.delete(0, tk.END)

    def leave_chat(self):
        leave_message = "!LEAVE"
        encrypted_message = cipher.encrypt(leave_message.encode())
        self.client_socket.send(encrypted_message)
        self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(2048)
                if message:
                    decrypted_message = cipher.decrypt(message).decode()
                    self.display_message(decrypted_message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def display_message(self, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + "\n")
        self.chat_log.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
