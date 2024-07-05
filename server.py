import socket
from threading import Thread
from cryptography.fernet import Fernet

# Server configuration
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 12345
MAX_CLIENTS = 5

# Load encryption key from file
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

clients = []

def handle_client(client_socket, address):
    try:
        # Receive username
        username = client_socket.recv(1024).decode()
        print(f"Username received: {username}")

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
                else:
                    remove(client_socket, username)
                    break
            except Exception as e:
                print(f"Error handling message from {username}: {e}")
                break
    except Exception as e:
        print(f"Error handling client {address}: {e}")
        client_socket.close()

def broadcast(message, username, exclude_user=None):
    global clients
    for client, user in clients:
        if user != exclude_user:
            try:
                encrypted_message = cipher.encrypt(f"{username}: {message}".encode())
                client.send(encrypted_message)
            except Exception as e:
                print(f"Error broadcasting message to {user}: {e}")
                remove(client, user)

def remove(client, username):
    global clients
    for c, user in clients:
        if c == client:
            clients.remove((c, user))
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)

    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    main()
