import socket
import ssl
import threading
import sqlite3
from cryptography.fernet import Fernet
import pyotp

# Server configuration
HOST = '127.0.0.1'
PORT = 12345
MAX_CLIENTS = 5

# Load encryption key from file
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# Load OTP secret from file
with open("otp_secret.txt", "r") as secret_file:
    otp_secret = secret_file.read().strip()

totp = pyotp.TOTP(otp_secret)

# Initialize database for chat history
conn = sqlite3.connect('chat_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history
             (user TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()
conn.close()

clients = []
user_status = {}


def handle_client(client_socket, address):
    global clients

    # Create a new SQLite connection for this thread
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()

    try:
        # Receive username
        username = client_socket.recv(1024).decode()
        print(f"Username received: {username}")

        # Receive OTP for validation
        otp = client_socket.recv(1024).decode()
        print(f"OTP received: {otp}")
        if not totp.verify(otp):
            print(f"Invalid OTP from {username}")
            client_socket.send("Invalid OTP".encode())
            client_socket.close()
            return

        user_status[username] = 'online'
        clients.append((client_socket, username))
        client_socket.send("Authentication successful".encode())

        # Broadcast welcome message
        welcome_message = f"{username} has joined the chat."
        broadcast(welcome_message, username)

        while True:
            try:
                message = client_socket.recv(2048)
                if message:
                    decrypted_message = cipher.decrypt(message).decode()
                    if decrypted_message == "!LEAVE":
                        user_left_message = f"{username} has left the chat."
                        broadcast(user_left_message, username, exclude_user=username)
                        remove(client_socket, username)
                        break
                    broadcast(decrypted_message, username)
                    save_message(c, username, decrypted_message)
                else:
                    remove(client_socket, username)
                    break
            except Exception as e:
                print(f"Error handling message from {username}: {e}")
                break
    except Exception as e:
        print(f"Error handling client {address}: {e}")
        client_socket.close()
    finally:
        conn.close()


def broadcast(message, username, exclude_user=None):
    global clients
    for client, user in clients:
        if user != exclude_user:
            try:
                encrypted_message = cipher.encrypt(f"{username}: {message}".encode())
                client.send(encrypted_message)
            except:
                remove(client, user)


def save_message(c, username, message):
    c.execute("INSERT INTO history (user, message) VALUES (?, ?)", (username, message))
    c.connection.commit()


def remove(client, username):
    global clients
    for c, user in clients:
        if c == client:
            clients.remove((c, user))
            user_status[user] = 'offline'
            break


def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)

    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        try:
            client_socket = context.wrap_socket(client_socket, server_side=True)
            print(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()
        except ssl.SSLError as e:
            print(f"SSL error with client {addr}: {e}")
            client_socket.close()


if __name__ == "__main__":
    main()
