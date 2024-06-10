import pyotp
import qrcode

# Generate a base32 secret
secret = pyotp.random_base32()
print("Your new OTP secret is:", secret)

# Generate a QR code URL
otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name='user@example.com', issuer_name='SecureChatApp')
print("Scan this QR code in your OTP app:")
print(otp_uri)

# Generate QR code image
img = qrcode.make(otp_uri)
img.save("otp_qr.png")
img.show()

# Save the secret to a file for later use
with open("otp_secret.txt", "w") as secret_file:
    secret_file.write(secret)
