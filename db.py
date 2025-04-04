import sqlite3, uuid, os
from encryption import encrypt_data, decrypt_data
DB_FILE = "voting_app.db"
TOKEN_FILE = "device_token.txt"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (token TEXT, vote_option TEXT, vote_date TEXT)''')
    conn.commit()
    conn.close()

def get_device_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read()
    token = str(uuid.uuid4())
    with open(TOKEN_FILE, "w") as file:
        file.write(token)
    return token

def user_exists(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def save_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, encrypt_data(password)))
    conn.commit()
    conn.close()

def fetch_user_password(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return decrypt_data(row[0]) if row else None

def delete_user_account(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
