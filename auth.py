from db import user_exists, save_user, fetch_user_password
import sqlite3
from encryption import hash_password, check_password
from tkinter import messagebox

def register_user(username, password):
    if user_exists(username):
        messagebox.showerror("Error", "The user already exists!")
        return False
    save_user(username, password)
    messagebox.showinfo("Success", "Registration successful!")
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect("voting_app.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password(password, row[0])
    return False