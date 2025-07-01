import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')
conn.commit()

def register():
    username = entry_username.get()
    password = entry_password.get()
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

def login():
    username = entry_username.get()
    password = entry_password.get()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        messagebox.showinfo("Success", "Login successful!")
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# GUI setup
root = tk.Tk()
root.title("Login/Register")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5)

tk.Button(root, text="Register", command=register).grid(row=2, column=0, padx=10, pady=10)
tk.Button(root, text="Login", command=login).grid(row=2, column=1, padx=10, pady=10)

root.mainloop()

conn.close()