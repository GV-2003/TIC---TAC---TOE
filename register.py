import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess
import sys
import os

# --- Color Palette ---
WIN_BG = "#87CEEB"         # Sky blue background for entire window
FRAME_BG = "#FFFFFF"       # White background for content frames
BTN_PRIMARY_BG = "#1976D2" # Blue buttons
BTN_PRIMARY_FG = "white"
BTN_SECONDARY_BG = "#4CAF50" # Green buttons
BTN_SECONDARY_FG = "white"
ENTRY_BG = "#E3F2FD"       # Light blue entry background
TEXT_FG = "#212121"        # Dark charcoal text
LABEL_FG = "#424242"       # Slightly lighter text for labels

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert a default user if none exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))

    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- Authenticate User ---
def authenticate_user():
    username = login_username_entry.get()
    password = login_password_entry.get()

    if not username or not password:
        messagebox.showerror("Input Error", "Both fields are required!")
        return

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
        login_window.destroy()
        home_page(username)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# --- Register Window ---
def open_register_window():
    register_win = tk.Toplevel()
    register_win.title("Register New User")
    register_win.geometry("400x400")
    register_win.configure(bg=WIN_BG)

    # Frame for content
    frame = tk.Frame(register_win, bg=FRAME_BG, padx=30, pady=30)
    frame.pack(expand=True, fill='both')

    tk.Label(frame, text="Register", font=("Helvetica", 24), bg=FRAME_BG, fg=TEXT_FG).pack(pady=20)

    tk.Label(frame, text="Username:", font=("Helvetica", 16), bg=FRAME_BG, fg=LABEL_FG).pack(anchor='w')
    new_username_entry = tk.Entry(frame, font=("Helvetica", 16), bg=ENTRY_BG, fg=TEXT_FG, relief='flat')
    new_username_entry.pack(pady=10, fill='x')

    tk.Label(frame, text="Password:", font=("Helvetica", 16), bg=FRAME_BG, fg=LABEL_FG).pack(anchor='w')
    new_password_entry = tk.Entry(frame, show="*", font=("Helvetica", 16), bg=ENTRY_BG, fg=TEXT_FG, relief='flat')
    new_password_entry.pack(pady=10, fill='x')

    def register_user():
        username = new_username_entry.get()
        password = new_password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            register_win.destroy()
            login_window.destroy()
            home_page(username)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    tk.Button(frame, text="Register", font=("Helvetica", 16),
              bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
              activebackground="#388E3C", activeforeground="white",
              relief='flat', command=register_user).pack(pady=20, fill='x')

# --- Home Page ---
def home_page(username):
    home_window = tk.Tk()
    home_window.title(f"Welcome {username} to Tic-Tac-Toe!")
    home_window.attributes('-fullscreen', True)
    home_window.configure(bg=WIN_BG)

    def exit_fullscreen(event):
        home_window.attributes('-fullscreen', False)

    home_window.bind("<Escape>", exit_fullscreen)
    home_window.focus_set()

    frame = tk.Frame(home_window, bg=FRAME_BG, padx=50, pady=50)
    frame.pack(expand=True)

    title_label = tk.Label(frame, text=f"Welcome, {username}!", font=("Helvetica", 32), bg=FRAME_BG, fg=TEXT_FG)
    title_label.pack(pady=40)

    start_game_button = tk.Button(frame, text="Start New Game", font=("Helvetica", 20),
                                  bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
                                  activebackground="#388E3C", activeforeground="white",
                                  relief='flat', command=lambda: start_game(username))
    start_game_button.pack(pady=20, fill='x')

    high_scores_button = tk.Button(frame, text="View High Scores", font=("Helvetica", 20),
                                   bg=BTN_PRIMARY_BG, fg=BTN_PRIMARY_FG,
                                   activebackground=BTN_PRIMARY_BG, activeforeground="white",
                                   relief='flat', command=view_high_scores)
    high_scores_button.pack(pady=20, fill='x')

    logout_button = tk.Button(frame, text="Log Out", font=("Helvetica", 20),
                              bg="#E53935", fg="white",
                              activebackground="#AB000D", activeforeground="white",
                              relief='flat', command=lambda: logout(home_window))
    logout_button.pack(pady=20, fill='x')

    home_window.mainloop()

def logout(window):
    window.destroy()
    # Restart login window
    global login_window
    login_window = create_login_window()
    login_window.mainloop()

def create_login_window():
    win = tk.Tk()
    win.title("Tic-Tac-Toe Login")
    win.attributes('-fullscreen', True)
    win.configure(bg=WIN_BG)

    def exit_fullscreen(event):
        win.attributes('-fullscreen', False)

    win.bind("<Escape>", exit_fullscreen)
    win.focus_set()

    frame = tk.Frame(win, bg=FRAME_BG, padx=50, pady=50)
    frame.pack(expand=True)

    tk.Label(frame, text="Login to Tic-Tac-Toe", font=("Helvetica", 32), bg=FRAME_BG, fg=TEXT_FG).pack(pady=40)

    tk.Label(frame, text="Username:", font=("Helvetica", 24), bg=FRAME_BG, fg=LABEL_FG).pack(anchor='w', pady=(0,5))
    global login_username_entry
    login_username_entry = tk.Entry(frame, font=("Helvetica", 24), width=20, bg=ENTRY_BG, fg=TEXT_FG, relief='flat')
    login_username_entry.pack(pady=(0,20), fill='x')

    tk.Label(frame, text="Password:", font=("Helvetica", 24), bg=FRAME_BG, fg=LABEL_FG).pack(anchor='w', pady=(0,5))
    global login_password_entry
    login_password_entry = tk.Entry(frame, font=("Helvetica", 24), show="*", width=20, bg=ENTRY_BG, fg=TEXT_FG, relief='flat')
    login_password_entry.pack(pady=(0,20), fill='x')

    tk.Button(frame, text="Login", font=("Helvetica", 20),
              bg=BTN_PRIMARY_BG, fg=BTN_PRIMARY_FG,
              activebackground=BTN_PRIMARY_BG, activeforeground="white",
              relief='flat', command=authenticate_user).pack(pady=30, fill='x')

    tk.Button(frame, text="Register", font=("Helvetica", 18),
              bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
              activebackground="#388E3C", activeforeground="white",
              relief='flat', command=open_register_window).pack(pady=10, fill='x')

    return win

# --- Start Game ---
def start_game(username):
    # Check if game.py exists in the current directory
    if os.path.exists("game.py"):
        try:
            # Run the game.py with username argument
            result = subprocess.run([sys.executable, "game.py", username], capture_output=True, text=True)
            
            # Check if the subprocess ran successfully
            if result.returncode != 0:
                messagebox.showerror("Game Error", f"Error in starting the game:\n{result.stderr}")
            else:
                # Game started successfully (output can be logged or processed if needed)
                pass
        except Exception as e:
            messagebox.showerror("Game Error", f"An unexpected error occurred while starting the game:\n{str(e)}")
    else:
        messagebox.showerror("Game Not Found", "game.py not found in the current directory!")

# --- View High Scores ---
def view_high_scores():
    try:
        conn = sqlite3.connect('tictactoe.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                winner, COUNT(*) AS wins 
            FROM scores 
            GROUP BY winner 
            ORDER BY wins DESC
        ''')
        results = cursor.fetchall()
        conn.close()

        if not results:
            messagebox.showinfo("High Scores", "No game results recorded yet.")
            return

        score_text = "🏆 High Scores:\n\n"
        for winner, count in results:
            player = "Draws" if winner == "None" else winner
            score_text += f"{player}: {count} win(s)\n"

        messagebox.showinfo("High Scores", score_text)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch scores:\n{e}")

# --- Run the Login Window ---
login_window = create_login_window()
login_window.mainloop()

# Close DB on exit
conn.close()
