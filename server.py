import socket
import threading
import select

# User database (for simplicity, using a dictionary; in production, use a secure database)
users = {"user1": "password1", "user2": "password2"}
clients = {}

def broadcast(message, exclude_client=None):
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message.encode())
            except:
                clients.pop(client)
                client.close()

def handle_client(client_socket, addr):
    authenticated = False
    username = None

    client_socket.send("Welcome! Please log in.\n".encode())

    while not authenticated:
        try:
            client_socket.send("Username: ".encode())
            username = client_socket.recv(1024).decode().strip()
            client_socket.send("Password: ".encode())
            password = client_socket.recv(1024).decode().strip()

            if username in users and users[username] == password:
                client_socket.send("Login successful! Welcome to the chat room.\n".encode())
                broadcast(f"{username} has joined the chat.", client_socket)
                authenticated = True
                clients[client_socket] = username
            else:
                client_socket.send("Invalid credentials. Try again.\n".encode())
        except:
            client_socket.close()
            return

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                if message.startswith("@"):
                    target_username, private_message = message.split(" ", 1)
                    target_username = target_username[1:]
                    for client, name in clients.items():
                        if name == target_username:
                            client.send(f"Private from {username}: {private_message}".encode())
                            break
                else:
                    broadcast(f"{username}: {message}", client_socket)
            else:
                clients.pop(client_socket)
                client_socket.close()
                broadcast(f"{username} has left the chat.")
                break
        except:
            clients.pop(client_socket)
            client_socket.close()
            broadcast(f"{username} has left the chat.")
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("Server started, waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")

        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    main()
