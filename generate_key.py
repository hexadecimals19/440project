from cryptography.fernet import Fernet #Import the fernet in crypto library

# Generate a new encryption key
key = Fernet.generate_key()

# Save the key to a file, wb write-binary mode, generated enc key will write to the file
with open("secret.key", "wb") as key_file: #With statement ensure file properly close after write the ky at the file
    key_file.write(key)

print("Key generated and saved to secret.key") #print confirmation message
