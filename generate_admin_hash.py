import bcrypt

password = "Vignesh@5677"

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

print(hashed.decode())