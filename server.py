# Imports and Configuration
import socket #Used for creating network connections
from threading import Thread # Allows concurrent execution using threads
from cryptography.fernet import Fernet # Provides encryption functionalities


# Server configuration
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 12345 # Port number for the server
MAX_CLIENTS = 5 # Maximum number of clients the server can handle simultaneously


# Load encryption key from file
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key) # Create a Fernet cipher object for encryption and decryption


clients = [] # List to store connected clients

# Function to handle each client connection
def handle_client(client_socket, address):
    try:
        # Receive username from the client
        username = client_socket.recv(1024).decode()
        print(f"Username received: {username}")

        clients.append((client_socket, username)) # Add client socket and username to clients list
        client_socket.send("Authentication successful".encode()) # Send confirmation to client


        # Broadcast welcome message to all clients
        welcome_message = f"{username} has joined the chat."
        broadcast(welcome_message, username)

        while True:
            try:
                message = client_socket.recv(2048) # Receive message from client
                if message:
                    decrypted_message = cipher.decrypt(message).decode()  # Decrypt the received message
                    if decrypted_message == "!LEAVE":

                        # Handle client leaving the chat
                        user_left_message = f"{username} has left the chat."
                        broadcast(user_left_message, username, exclude_user=username)
                        remove(client_socket, username) # Remove client from clients list
                        break
                    broadcast(decrypted_message, username) # Broadcast message to all clients
                else:
                    remove(client_socket, username) # Remove client from clients list if no message received
                    break
            except Exception as e:
                print(f"Error handling message from {username}: {e}")
                break
    except Exception as e:
        print(f"Error handling client {address}: {e}")
        client_socket.close() # Close client socket in case of error

# Function to broadcast message to all clients
def broadcast(message, username, exclude_user=None):
    global clients
    for client, user in clients:
        if user != exclude_user:
            try:
                encrypted_message = cipher.encrypt(f"{username}: {message}".encode()) # Encrypt message

                client.send(encrypted_message)  # Send encrypted message to client
            except Exception as e:
                print(f"Error broadcasting message to {user}: {e}")
                remove(client, user) # Remove client from clients list in case of error

# Function to remove client from clients list
def remove(client, username):
    global clients
    for c, user in clients:
        if c == client:
            clients.remove((c, user)) # Remove client from clients list

            break

# Main function to start the server
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP socket for server
    server.bind((HOST, PORT)) # Bind socket to host and port
    server.listen(MAX_CLIENTS) # Start listening for client connections


    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept() # Accept client connection
        print(f"Connection from {addr}")
        Thread(target=handle_client, args=(client_socket, addr)).start() # Start a new thread for each client


if __name__ == "__main__":
    main() # Call main function if script is executed directly
