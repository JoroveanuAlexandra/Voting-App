import sqlite3, uuid
from encryption import encrypt_data, decrypt_data
from encryption import hash_password, check_password

DB_FILE = "voting_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (token TEXT, vote_option TEXT, vote_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS device_tokens (token TEXT PRIMARY KEY)''')  # New table for device tokens
    conn.commit()
    conn.close()

def get_device_token():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT token FROM device_tokens LIMIT 1")
    row = c.fetchone()

    if row:
        token = row[0]  
    else:
        token = str(uuid.uuid4()) 
        c.execute("INSERT INTO device_tokens (token) VALUES (?)", (token,))  # Save the new token
        conn.commit()

    conn.close()
    return token

def user_exists(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def save_user(username, password):
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
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
