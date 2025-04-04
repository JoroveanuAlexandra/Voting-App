import tkinter as tk
from tkinter import messagebox
from auth import authenticate_user, register_user
from voting import has_voted_today, save_vote, get_vote_counts
from db import init_db
from ui_config import DEFAULT_BG_COLOR, DEFAULT_FONT, BUTTON_STYLE
from db import delete_user_account
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def vote(option, username, voting_window, login_window):
    if username == "anonim":
        if has_voted_today("anonim"):
            messagebox.showwarning("Voting", "You have already voted today from this device.")
            voting_window.destroy()
            login_window.deiconify()
            return
        save_vote(option, "anonim")
    else:
        save_vote(option, username)

    messagebox.showinfo("Voting", f"You voted for: {option}")
    voting_window.destroy()
    login_window.username_entry.delete(0, tk.END)
    login_window.password_entry.delete(0, tk.END)
    login_window.deiconify()


def on_login_button_click(username_entry, password_entry, login_window):
    username = username_entry.get()
    password = password_entry.get()
    if authenticate_user(username, password):
        if username == "admin":
            open_admin_window(login_window)
        else:
            open_user_dashboard(login_window, username)
    else:
        messagebox.showerror("Error", "Invalid login credentials!")

def on_register_button_click(username_entry, password_entry, register_window):
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Error", "Please fill out all fields!")
        return
    if register_user(username, password):
        register_window.destroy()


def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.configure(bg=DEFAULT_BG_COLOR)

def create_register_window():
    register_window = tk.Toplevel()
    register_window.title("User Registration")
    center_window(register_window, 400, 300)

    tk.Label(register_window, text="Username:", font=DEFAULT_FONT, bg=DEFAULT_BG_COLOR).pack(pady=10)
    username_entry = tk.Entry(register_window, font=DEFAULT_FONT)
    username_entry.pack(pady=5)

    tk.Label(register_window, text="Password:", font=DEFAULT_FONT, bg=DEFAULT_BG_COLOR).pack(pady=10)
    password_entry = tk.Entry(register_window, show="*", font=DEFAULT_FONT)
    password_entry.pack(pady=5)

    tk.Button(register_window, text="Register", **BUTTON_STYLE, command=lambda: on_register_button_click(username_entry, password_entry, register_window)).pack(pady=20)

def create_login_window():
    login_window = tk.Tk()
    login_window.title("User Login")
    center_window(login_window, 400, 350)

    tk.Label(login_window, text="Username:", font=DEFAULT_FONT, bg=DEFAULT_BG_COLOR).pack(pady=10)
    username_entry = tk.Entry(login_window, font=DEFAULT_FONT)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:", font=DEFAULT_FONT, bg=DEFAULT_BG_COLOR).pack(pady=10)
    password_entry = tk.Entry(login_window, show="*", font=DEFAULT_FONT)
    password_entry.pack(pady=5)

    login_window.username_entry = username_entry
    login_window.password_entry = password_entry

    tk.Button(login_window, text="Login", **BUTTON_STYLE,
              command=lambda: on_login_button_click(username_entry, password_entry, login_window)).pack(pady=10)

    tk.Button(login_window, text="Register", **BUTTON_STYLE,
              command=create_register_window).pack(pady=10)

    tk.Button(login_window, text="Vote Anonymously", **BUTTON_STYLE,
              command=lambda: [login_window.withdraw(), open_voting_window(login_window, "anonim")]).pack(pady=10)

    login_window.mainloop()

def open_voting_window(login_window, username):
    login_window.withdraw()

    if username == "admin":
        open_admin_window(login_window)
        return

    voting_window = tk.Toplevel(login_window)
    voting_window.title("Voting Window")
    center_window(voting_window, 400, 400)

    tk.Label(voting_window, text="Choose your option:", font=("Comic Sans MS", 14, "bold"), bg=DEFAULT_BG_COLOR).pack(pady=20)

    for option in ["Option 1", "Option 2", "Option 3", "Option 4"]:
        tk.Button(voting_window, text=option, **BUTTON_STYLE,
                  command=lambda opt=option: vote(opt, username, voting_window, login_window)).pack(pady=10)


def open_admin_window(login_window):
    admin_results_window = tk.Toplevel()
    admin_results_window.title("Voting Results")
    center_window(admin_results_window, 600, 500)

    tk.Label(admin_results_window, text="Voting Results", font=("Comic Sans MS", 16, "bold"), bg=DEFAULT_BG_COLOR).pack(pady=10)

    chart_frame = tk.Frame(admin_results_window, bg=DEFAULT_BG_COLOR)
    chart_frame.pack(pady=10)

    chart_canvas = [None]

    def draw_chart():
        if chart_canvas[0]:
            chart_canvas[0].get_tk_widget().destroy()

        votes_count = get_vote_counts()
        options = list(votes_count.keys())
        counts = list(votes_count.values())

        fig, ax = plt.subplots(figsize=(5, 3))
        bars = ax.bar(options, counts, color=["#007BFF", "#28A745", "#FFC107", "#DC3545"])
        ax.set_ylabel("Number of Votes")
        ax.set_title("Vote Distribution")

        max_votes = max(counts) if counts else 0
        ax.set_ylim(0, max_votes + 1)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

        chart_canvas[0] = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas[0].draw()
        chart_canvas[0].get_tk_widget().pack()

    draw_chart()

    tk.Button(admin_results_window, text="Refresh Results", **BUTTON_STYLE, command=draw_chart).pack(pady=10)

    def logout():
        admin_results_window.destroy()
        login_window.username_entry.delete(0, tk.END)
        login_window.password_entry.delete(0, tk.END)
        login_window.deiconify()

    tk.Button(admin_results_window, text="Logout", **BUTTON_STYLE, command=logout).pack(pady=10)


def open_user_dashboard(login_window, username):
    login_window.withdraw()
    dashboard = tk.Toplevel()
    dashboard.title("User Dashboard")
    center_window(dashboard, 400, 300)

    tk.Label(dashboard, text=f"Welcome, {username}!", font=("Comic Sans MS", 14, "bold"), bg=DEFAULT_BG_COLOR).pack(pady=20)

    if not has_voted_today(username):
        tk.Button(dashboard, text="Vote", **BUTTON_STYLE,
                  command=lambda: [dashboard.destroy(), open_voting_window(login_window, username)]).pack(pady=10)
    else:
        tk.Label(dashboard, text="You have already voted today.", font=DEFAULT_FONT, bg=DEFAULT_BG_COLOR).pack(pady=10)

    if username != "admin":
        def delete_account():
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete your account?")
            if confirm:
                delete_user_account(username)
                messagebox.showinfo("Account Deleted", "Your account has been deleted.")
                dashboard.destroy()
                login_window.deiconify()
                login_window.username_entry.delete(0, tk.END)
                login_window.password_entry.delete(0, tk.END)

        tk.Button(dashboard, text="Delete Account", **BUTTON_STYLE, command=delete_account).pack(pady=10)

    tk.Button(dashboard, text="Logout", **BUTTON_STYLE,
              command=lambda: [dashboard.destroy(), login_window.username_entry.delete(0, tk.END),
                               login_window.password_entry.delete(0, tk.END), login_window.deiconify()]).pack(pady=10)


if __name__ == "__main__":
    init_db()
    create_login_window()
