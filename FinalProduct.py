import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import pandas as pd
import random
import os

# --- Data Setup ---
MOVIE_CSV = r'c:\Users\harri\Desktop\Software project\ml-latest\movies.csv'

# Try to load the CSV, but don't block the GUI if it fails
movies_df = None
try:
    if not os.path.exists(MOVIE_CSV):
        raise FileNotFoundError("movies.csv not found at expected location.")
    movies_df = pd.read_csv(MOVIE_CSV)
    print("Loaded movies:", len(movies_df))
except Exception as e:
    print("Error loading movies.csv:", e)
    movies_df = pd.DataFrame(columns=['movieId', 'title', 'genres'])

GENRES = [
    "Comedy", "Thriller", "Drama", "Romance", "Documentary", "Adventure",
    "Crime", "Action", "Children", "Horror", "War", "Musical", "Fantasy", "Western", "Sci-Fi"
]
EMOTION_GENRE_MAP = {
    "Sad": "Comedy",
    "Happy": "Adventure",
    "Angry": "Action",
    "Bored": "Thriller",
    "Romantic": "Romance",
    "Curious": "Documentary",
    "Scared": "Horror",
    "Nostalgic": "Drama"
}

# --- Database Setup ---
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        username TEXT,
        movieId INTEGER,
        rating INTEGER,
        PRIMARY KEY (username, movieId)
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
        messagebox.showinfo("Success", f"Login successful! Welcome, {username}.")
        root.withdraw()
        show_main_window(username)
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def show_main_window(username):
    main_win = tk.Toplevel()
    main_win.title(f"Movie Selector - {username}")

    def logout():
        main_win.destroy()
        root.deiconify()

    # --- Movie Rating Section ---
    rating_frame = tk.LabelFrame(main_win, text="Rate Movies")
    rating_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(rating_frame, text="Search for a movie:").grid(row=0, column=0, padx=5, pady=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(rating_frame, textvariable=search_var, width=40)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    movie_listbox = tk.Listbox(rating_frame, width=50, height=5)
    movie_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def search_movies():
        query = search_var.get().strip().lower()
        movie_listbox.delete(0, tk.END)
        if not query:
            return
        if movies_df is None or movies_df.empty:
            messagebox.showerror("Error", "Movie database not loaded.")
            return
        matches = movies_df[movies_df['title'].str.lower().str.contains(query)]
        for title in matches['title'].tolist():
            movie_listbox.insert(tk.END, title)

    search_btn = tk.Button(rating_frame, text="Search", command=search_movies)
    search_btn.grid(row=0, column=2, padx=5, pady=5)

    tk.Label(rating_frame, text="Your rating (1-5):").grid(row=2, column=0, padx=5, pady=5)
    rating_var = tk.IntVar(value=5)
    rating_entry = tk.Spinbox(rating_frame, from_=1, to=5, textvariable=rating_var, width=5)
    rating_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit_rating():
        selection = movie_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a movie from the list.")
            return
        movie_title = movie_listbox.get(selection[0])
        rating = rating_var.get()
        movie_row = movies_df[movies_df['title'] == movie_title]
        if movie_row.empty:
            messagebox.showerror("Error", "Movie not found.")
            return
        movie_id = int(movie_row['movieId'].values[0])
        # Save rating for this user and movie
        c.execute("REPLACE INTO ratings (username, movieId, rating) VALUES (?, ?, ?)", (username, movie_id, rating))
        conn.commit()
        messagebox.showinfo("Success", f"Rated '{movie_title}' with {rating} stars.")

    tk.Button(rating_frame, text="Submit Rating", command=submit_rating).grid(row=3, column=0, columnspan=2, pady=5)

    # --- Personalized Recommendation Section ---
    def recommend_movies():
        c.execute("SELECT movieId, rating FROM ratings WHERE username=?", (username,))
        user_ratings = c.fetchall()
        if not user_ratings:
            messagebox.showinfo("Info", "Rate some movies first for recommendations!")
            return
        genre_scores = {}
        genre_counts = {}
        for movie_id, rating in user_ratings:
            genres = movies_df[movies_df['movieId'] == movie_id]['genres'].values
            if genres:
                for genre in genres[0].split('|'):
                    genre_scores[genre] = genre_scores.get(genre, 0) + rating
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        if not genre_scores:
            messagebox.showinfo("Info", "No genre data found.")
            return
        # Calculate average ratings for each genre
        genre_averages = {genre: genre_scores[genre] / genre_counts[genre] for genre in genre_scores}
        top_genres = sorted(genre_averages, key=genre_averages.get, reverse=True)[:2]
        rated_ids = [movie_id for movie_id, _ in user_ratings]
        recommendations = movies_df[
            (movies_df['genres'].str.contains('|'.join(top_genres))) &
            (~movies_df['movieId'].isin(rated_ids))
        ]
        if recommendations.empty:
            messagebox.showinfo("Info", "No new recommendations found. Try rating more movies!")
            return
        rec_sample = recommendations.sample(n=min(5, len(recommendations)))
        rec_text = "\n".join(rec_sample['title'].tolist())
        messagebox.showinfo("Recommended Movies", f"Based on your ratings, try these:\n\n{rec_text}")

    tk.Button(rating_frame, text="Recommend Movies", command=recommend_movies).grid(row=4, column=0, columnspan=2, pady=5)

    # --- Random Selector by Genre ---
    genre_frame = tk.LabelFrame(main_win, text="Random Movie by Genre")
    genre_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(genre_frame, text="Select genre:").grid(row=0, column=0, padx=5, pady=5)
    genre_var = tk.StringVar(value=GENRES[0])
    genre_menu = tk.OptionMenu(genre_frame, genre_var, *GENRES)
    genre_menu.grid(row=0, column=1, padx=5, pady=5)

    def random_by_genre():
        genre = genre_var.get()
        if movies_df is None or movies_df.empty:
            messagebox.showerror("Error", "Movie database not loaded.")
            return
        filtered = movies_df[movies_df['genres'].str.contains(genre, case=False, na=False)]
        if filtered.empty:
            messagebox.showinfo("No Movies", f"No movies found for genre: {genre}")
            return
        sample = filtered.sample(n=min(5, len(filtered)))
        text = "\n".join(sample['title'].tolist())
        messagebox.showinfo("Random Movies", f"Random {genre} movies:\n\n{text}")

    tk.Button(genre_frame, text="Show Random Movies", command=random_by_genre).grid(row=1, column=0, columnspan=2, pady=5)

    # --- Random Selector by Emotion ---
    emotion_frame = tk.LabelFrame(main_win, text="Random Movie by Emotion")
    emotion_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(emotion_frame, text="Select emotion:").grid(row=0, column=0, padx=5, pady=5)
    emotion_var = tk.StringVar(value=list(EMOTION_GENRE_MAP.keys())[0])
    emotion_menu = tk.OptionMenu(emotion_frame, emotion_var, *EMOTION_GENRE_MAP.keys())
    emotion_menu.grid(row=0, column=1, padx=5, pady=5)

    def random_by_emotion():
        emotion = emotion_var.get()
        genre = EMOTION_GENRE_MAP[emotion]
        if movies_df is None or movies_df.empty:
            messagebox.showerror("Error", "Movie database not loaded.")
            return
        filtered = movies_df[movies_df['genres'].str.contains(genre, case=False, na=False)]
        if filtered.empty:
            messagebox.showinfo("No Movies", f"No movies found for emotion: {emotion} ({genre})")
            return
        sample = filtered.sample(n=min(5, len(filtered)))
        text = "\n".join(sample['title'].tolist())
        messagebox.showinfo("Random Movies", f"Because you're {emotion}, try these {genre} movies:\n\n{text}")

    tk.Button(emotion_frame, text="Show Random Movies", command=random_by_emotion).grid(row=1, column=0, columnspan=2, pady=5)

    # --- Logout Button ---
    tk.Button(main_win, text="Logout", command=logout, fg="red").grid(row=3, column=0, pady=10)

# --- Main Login/Register Window ---
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
