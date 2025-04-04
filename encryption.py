import os, base64
import bcrypt
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

load_dotenv()
key_from_env = os.environ.get("VOTING_APP_AES_KEY")
if not key_from_env:
    raise ValueError("Encryption key not found. Please set the VOTING_APP_AES_KEY environment variable.")
ENCRYPTION_KEY = key_from_env.encode('utf-8')

def encrypt_data(data):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    data = data.encode('utf-8')
    padded_data = data + (16 - len(data) % 16) * b" "
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_data(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.rstrip(b" ").decode('utf-8')

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
