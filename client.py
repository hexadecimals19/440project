# Imports and Configuration
import socket #Used for creating network connections
import tkinter as tk #Python GUI library
from tkinter import simpledialog #Provide simple dialog boxes for user input
from cryptography.fernet import Fernet # Used for symmetric encryption and decryption
from threading import Thread #Used to run many task in concurrently in separate threads


HOST = '192.168.1.177' #Spesifcy the Server IP (Ubuntu)
PORT = 8080 #Port Num which server will listen

# Load encryption key from file
with open("secret.key", "rb") as key_file: #File have symmetric encryption key
    key = key_file.read() #Load the Encryption key to key variable
cipher = Fernet(key) #An instance of Fernet initialized with the loaded encryption key

class ChatClient: #ChatClient Class
    def __init__(self, master): #Root window of Tkinter App
        self.master = master
        self.master.title("RTSCL V1.0") #Sets the title of the window.

        self.chat_log = tk.Text(master, state='disabled') #Tkinter text widget to display chat messages, state='disabled' makes the text widget read only
        self.chat_log.pack() # .pack places the widget in the window

        self.message_entry = tk.Entry(master) #Tkinter entry widget for typing messages
        self.message_entry.pack() #.pack places the message entry in the window
        self.message_entry.bind("<Return>", self.send_message) #calls send_message method when the return key is pressed, bind will be the action when press return, the send message will occur

        self.leave_button = tk.Button(master, text="Leave RTSCL", command=self.leave_chat) #tkinter button widget to leave the chat, calls leave_chat method when the button is pressed.
        self.leave_button.pack() #.pack places the button in the window


        self.username = simpledialog.askstring("Username", "Enter your Username") #Prompts the user to enter their username
        # Socket= Create the TCP/IP socket for connect to server, send, receive data
        #socket connection
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create TCP Socket, AF_INET will specifies Ipv4 and SOCK_STREAM will spesifices TCP
            self.client_socket.connect((HOST, PORT)) #Socket connect the spesified HOST and PORT
            self.client_socket.send(self.username.encode()) #Socket send the username to the server and encode it

            auth_response = self.client_socket.recv(1024).decode() #Check the authentication response from the server, get client socket and receives a message from the server until 1024byte,decode() will convert byte to string
            if auth_response != "Authentication successful": #if the authentication response is not "Authentication successful", then will print auth failed
                print("Authentication failed")
                self.master.destroy() #Closes the Tkinter GUI window
                return

            # Thread= Concurrent Execution
            #Parallel Processing=perform multi operataion concurrently

            Thread(target=self.receive_messages).start() #Starts a new thread to receive messages from the server

            self.display_message(f"Welcome to RTSCL, {self.username}!") # Display welcome message in the client chat window by their username

        #Error Handling
        except Exception as e: #handles exceptions during connection and authentication
            print(f"Error connecting to server: {e}") #print error message
            self.master.destroy() #close window if exceptions during connection and authentication

    # Advanced Socket= encrypted and decrypt communication and handling socket errors (Exception)
#Send Message Method
    def send_message(self, event):
        message = self.message_entry.get() #Gets the message from the entry widget.
        encrypted_message = cipher.encrypt(message.encode()) #Encrypt the string message
        self.client_socket.send(encrypted_message) #Socket send the encrypted message
        self.message_entry.delete(0, tk.END) #Clears the entry widget after send the message

    # Leave chat method
    def leave_chat(self):
        leave_message = "!LEAVE" #Sets the leave message (Username** leave the chat)
        encrypted_message = cipher.encrypt(leave_message.encode()) #Encrypt leave message
        self.client_socket.send(encrypted_message) #Send the encrypted message
        self.master.destroy() #Close the window

#Receive Message Method
    def receive_messages(self):
        while True: #Continuously receives messages.
            try:
                message = self.client_socket.recv(2048) #Receives a message from the server until 2048 byte
                if message:
                    decrypted_message = cipher.decrypt(message).decode() # Decrypts the byte to string message
                    self.display_message(decrypted_message) #Display decrypyted message
            except Exception as e: #Handles any exceptions during receiving messages
                print(f"Error receiving message: {e}") #Print error message
                break #Exit loop if error happen

#Display Message Method
    def display_message(self, message):
        self.chat_log.config(state='normal') #makes the chat log editable.
        self.chat_log.insert(tk.END, message + "\n")  #: Inserts the message into the chat log
        self.chat_log.config(state='disabled') #makes the chat log read-only again

if __name__ == "__main__": #Ensures this main runs only if the script is executed directly
    root = tk.Tk() #Creates the main application window
    client = ChatClient(root) #Create Chatclient refer to the chatclient class
    root.mainloop() #Starts the Tkinter event loop


#State normal= can editable
#State disabled= only can read
