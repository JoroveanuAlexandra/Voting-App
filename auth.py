from db import user_exists, save_user, fetch_user_password
from tkinter import messagebox

def register_user(username, password):
    if user_exists(username):
        messagebox.showerror("Error", "The user already exists!")
        return False
    save_user(username, password)
    messagebox.showinfo("Success", "Registration successful!")
    return True

def authenticate_user(username, password):
    stored_password = fetch_user_password(username)
    return stored_password == password
