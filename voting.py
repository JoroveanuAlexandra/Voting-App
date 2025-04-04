import sqlite3
from datetime import datetime
from encryption import encrypt_data, decrypt_data
from db import get_device_token
import hashlib

DB_FILE = "voting_app.db"

def generate_daily_token(identifier):
    today = datetime.now().strftime('%Y-%m-%d')
    raw = f"{identifier}-{today}"
    return hashlib.sha256(raw.encode()).hexdigest()

def has_voted_today(username):
    if username == "anonim":
        identifier = get_device_token()
    else:
        identifier = username

    token = generate_daily_token(identifier)
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM votes WHERE token = ? AND vote_date = ?", (token, today))
    voted = c.fetchone() is not None
    conn.close()
    return voted


def save_vote(option, username="anonim"):
    identifier = get_device_token() if username == "anonim" else username
    token = generate_daily_token(identifier)
    today = datetime.now().strftime('%Y-%m-%d')

    encrypted_vote = encrypt_data(option)  

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO votes (token, vote_option, vote_date) VALUES (?, ?, ?)", (token, encrypted_vote, today))
    conn.commit()
    conn.close()


def get_vote_counts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT vote_option FROM votes")
    encrypted_votes = c.fetchall()
    conn.close()
    decrypted_votes = [decrypt_data(vote[0]) for vote in encrypted_votes]

    return {
        "Option 1": decrypted_votes.count("Option 1"),
        "Option 2": decrypted_votes.count("Option 2"),
        "Option 3": decrypted_votes.count("Option 3"),
        "Option 4": decrypted_votes.count("Option 4"),
    }