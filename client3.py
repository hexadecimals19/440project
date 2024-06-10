import socket
import ssl
import tkinter as tk
from tkinter import simpledialog
from cryptography.fernet import Fernet
import pyotp
import threading

# Client configuration
HOST = '127.0.0.1'
PORT = 12345

# Load encryption key from file
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# Load OTP secret from file
with open("otp_secret.txt", "r") as secret_file:
    otp_secret = secret_file.read().strip()

totp = pyotp.TOTP(otp_secret)


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Chat Client")

        self.chat_log = tk.Text(master, state='disabled')
        self.chat_log.pack()

        self.message_entry = tk.Entry(master)
        self.message_entry.pack()
        self.message_entry.bind("<Return>", self.send_message)

        self.leave_button = tk.Button(master, text="Leave Chat", command=self.leave_chat)
        self.leave_button.pack()

        self.username = simpledialog.askstring("Username", "Enter your username")

        # Prompt for OTP
        otp = simpledialog.askstring("2FA", "Enter the OTP")
        if not self.authenticate(otp):
            print("Authentication failed")
            self.master.destroy()
            return

        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('cert.pem')

        try:
            self.client_socket = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                                          server_hostname=HOST)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.username.encode())
            self.client_socket.send(otp.encode())

            auth_response = self.client_socket.recv(1024).decode()
            if auth_response != "Authentication successful":
                print("Authentication failed")
                self.master.destroy()
                return

            threading.Thread(target=self.receive_messages).start()

            # Display welcome message in the client's own chat window
            self.display_message(f"Welcome, {self.username}!")

        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            self.master.destroy()
        except ConnectionResetError as e:
            print(f"Connection error: {e}")
            self.master.destroy()

    def authenticate(self, otp):
        return totp.verify(otp)

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
