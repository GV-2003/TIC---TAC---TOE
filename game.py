import tkinter as tk
from tkinter import messagebox
import sys
import sqlite3

# Get logged-in username passed as argument (or "Guest" fallback)
username = sys.argv[1] if len(sys.argv) > 1 else "Guest"

def record_score(winner_username):
    try:
        conn = sqlite3.connect('tictactoe.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scores (winner) VALUES (?)", (winner_username,))
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to record score:\n{e}")

def show_scores_summary():
    try:
        conn = sqlite3.connect('tictactoe.db')
        cursor = conn.cursor()

        # Select winners who exist in users table and count wins
        cursor.execute('''
            SELECT winner, COUNT(*) as wins
            FROM scores
            WHERE winner != "None" AND winner IN (SELECT username FROM users)
            GROUP BY winner
            ORDER BY wins DESC
        ''')
        results = cursor.fetchall()
        conn.close()

        if not results:
            messagebox.showinfo("High Scores", "No high scores from registered users yet.")
            return

        # Create fullscreen high score window
        hs_window = tk.Toplevel(game_window)
        hs_window.title("High Scores")
        hs_window.attributes('-fullscreen', True)
        hs_window.configure(bg=WINDOW_BG)

        def exit_fullscreen(event=None):
            hs_window.destroy()

        hs_window.bind("<Escape>", exit_fullscreen)

        container = tk.Frame(hs_window, bg=FRAME_BG, padx=40, pady=40, relief='raised', borderwidth=4)
        container.pack(expand=True, fill="both", padx=100, pady=100)

        title = tk.Label(container, text="🏆 Registered Users' High Scores 🏆",
                         font=("Helvetica", 40, 'bold'), bg=FRAME_BG, fg=TEXT_COLOR)
        title.pack(pady=(0,30))

        for player, wins in results:
            player_label = tk.Label(container, text=f"{player}: {wins} win(s)",
                                    font=("Helvetica", 28), bg=FRAME_BG, fg=TEXT_COLOR)
            player_label.pack(pady=10)

        close_btn = tk.Button(container, text="Close", font=("Helvetica", 20, 'bold'),
                              bg="#D32F2F", fg="white", padx=20, pady=10,
                              command=hs_window.destroy, cursor="hand2")
        close_btn.pack(pady=40)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch scores:\n{e}")

def reset_game():
    global current_player, moves_count, board
    current_player = "X"
    moves_count = 0
    board = [""] * 9
    update_turn_label()
    for btn in buttons:
        btn.config(text="", state="normal", bg=BUTTON_BG, disabledforeground='white')

def show_game_result(winner):
    if winner == "Draw":
        record_score("None")
        messagebox.showinfo("Result", "It's a draw!")
    else:
        # Store the username of logged-in player as winner
        record_score(username)
        messagebox.showinfo("Result", f"Player {winner} wins!")

    if messagebox.askyesno("Play Again?", "Do you want to play another game?"):
        reset_game()
    else:
        game_window.destroy()

def check_winner(player):
    wins = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    return any(all(board[i] == player for i in combo) for combo in wins)

def update_turn_label():
    turn_label.config(text=f"{current_player}'s Turn")
    turn_label.config(fg=PLAYER_X_COLOR if current_player == "X" else PLAYER_O_COLOR)

def button_click(index):
    global current_player, moves_count
    if board[index] == "":
        board[index] = current_player
        buttons[index].config(text=current_player, state='disabled', disabledforeground='white', bg=BUTTON_ACTIVE_BG)
        moves_count += 1

        if check_winner(current_player):
            show_game_result(current_player)
            return

        if moves_count == 9:
            show_game_result("Draw")
            return

        current_player = "O" if current_player == "X" else "X"
        update_turn_label()

def exit_fullscreen(event=None):
    game_window.attributes('-fullscreen', False)

# --- Colors ---
WINDOW_BG = "#cce7ff"          # Soft light blue
FRAME_BG = "white"             # White frame background
BUTTON_BG = "#4CAF50"          # Green buttons
BUTTON_ACTIVE_BG = "#388E3C"   # Darker green when clicked
BUTTON_HOVER_BG = "#45a049"    # Hover green (not used here)
PLAYER_X_COLOR = "#D32F2F"     # Red for player X
PLAYER_O_COLOR = "#1976D2"     # Blue for player O
TEXT_COLOR = "#333333"         # Dark gray text

# --- Main Window ---
game_window = tk.Tk()
game_window.title("Tic-Tac-Toe")
game_window.attributes('-fullscreen', True)
game_window.configure(bg=WINDOW_BG)
game_window.bind("<Escape>", exit_fullscreen)

main_frame = tk.Frame(game_window, bg=FRAME_BG, padx=40, pady=40, relief='raised', borderwidth=4)
main_frame.pack(expand=True)

title_label = tk.Label(main_frame, text="Tic-Tac-Toe", font=("Helvetica", 48, 'bold'), bg=FRAME_BG, fg=TEXT_COLOR)
title_label.pack(pady=30)

info_frame = tk.Frame(main_frame, bg=FRAME_BG)
info_frame.pack(pady=(0, 25))

user_label = tk.Label(info_frame, text=f"Player: {username}", font=("Helvetica", 20), bg=FRAME_BG, fg=TEXT_COLOR)
user_label.pack(side="left", padx=20)

turn_label = tk.Label(info_frame, text="", font=("Helvetica", 20, 'bold'), bg=FRAME_BG)
turn_label.pack(side="left", padx=20)

score_button = tk.Button(info_frame, text="View High Scores", command=show_scores_summary,
                         bg="#007acc", fg="white", font=("Helvetica", 14), relief='groove', padx=15, pady=5,
                         cursor="hand2")
score_button.pack(side="left", padx=20)

frame = tk.Frame(main_frame, bg=FRAME_BG)
frame.pack()

buttons = []
board = [""] * 9
current_player = "X"
moves_count = 0

for i in range(3):
    for j in range(3):
        idx = i * 3 + j
        btn = tk.Button(frame,
                        text="",
                        font=("Helvetica", 60, 'bold'),
                        width=3,
                        height=1,
                        bg=BUTTON_BG,
                        fg="white",
                        activebackground=BUTTON_ACTIVE_BG,
                        command=lambda idx=idx: button_click(idx),
                        relief='raised',
                        borderwidth=3,
                        highlightthickness=0,
                        cursor="hand2")
        btn.grid(row=i, column=j, padx=15, pady=15, sticky="nsew")
        buttons.append(btn)

update_turn_label()

game_window.mainloop()
