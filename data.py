import customtkinter as ctk
from PIL import Image
import json, os
from tkinter import messagebox, ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

FILE = "movies.json"

def load_movies():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_movies(movies):
    with open(FILE, "w") as f:
        json.dump(movies, f, indent=2)

def clear_email_placeholder(event):
    if email_entry.get() == "Email or phone number":
        email_entry.delete(0, "end")
        email_entry.configure(text_color="white")

def clear_password_placeholder(event):
    if password_entry.get() == "Password":
        password_entry.delete(0, "end")
        password_entry.configure(show="*", text_color="white")

def on_login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    if email == "" or email == "Email or phone number":
        messagebox.showwarning("Input Error", "Please enter your email or phone number.")
        return
    if password == "" or password == "Password":
        messagebox.showwarning("Input Error", "Please enter your password.")
        return
    login_window.destroy()
    root.deiconify()

def add_movie(event=None):
    title = title_var.get().strip()
    if title:
        movies.append({"title": title, "category": "General", "watched": False})
        save_movies(movies)
        update_list()
        title_var.set("")

def update_list(*args):
    search = search_var.get().strip().lower()
    tree.delete(*tree.get_children())
    for movie in movies:
        if search in movie["title"].lower():
            tree.insert("", "end", values=(movie["title"], movie.get("category", "General"), "Yes" if movie.get("watched") else "No"))

def clear_search():
    search_var.set("")
    update_list()

def mark_watched():
    selected = tree.selection()
    for item in selected:
        title = tree.item(item)["values"][0]
        for movie in movies:
            if movie["title"] == title:
                movie["watched"] = True
    save_movies(movies)
    update_list()

def delete_movie():
    selected = tree.selection()
    for item in selected:
        title = tree.item(item)["values"][0]
        for movie in movies:
            if movie["title"] == title:
                movies.remove(movie)
                break
    save_movies(movies)
    update_list()

def remove_search_placeholder(event):
    if search_entry.get() == "🔍 Search...":
        search_entry.delete(0, "end")
        search_entry.configure(text_color="white")

def add_search_placeholder(event):
    if search_entry.get() == "":
        search_entry.insert(0, "🔍 Search...")
        search_entry.configure(text_color="gray")

def show_all():
    update_list()

def show_continue_watchlist():
    tree.delete(*tree.get_children())
    for movie in movies:
        if not movie.get("watched"):
            tree.insert("", "end", values=(movie["title"], movie.get("category", "General"), "No"))

def show_category(cat):
    tree.delete(*tree.get_children())
    for movie in movies:
        if movie.get("category", "").lower() == cat.lower():
            tree.insert("", "end", values=(movie["title"], movie.get("category", "General"), "Yes" if movie.get("watched") else "No"))

def show_suggestions():
    messagebox.showinfo("Suggestions", "Try 'Interstellar', 'Naruto', 'KGF', or 'The Office'")

def show_history():
    messagebox.showinfo("History", "Feature Coming Soon!")

# --- Root Window ---
root = ctk.CTk()
root.title("MovieMAX")
root.geometry("1100x700")
root.configure(fg_color="#0D1D28")
root.withdraw()

# --- Login Window ---
login_window = ctk.CTkToplevel()
login_window.title("LOGIN - MovieMAX")
login_window.geometry("1000x600")

bg_image = Image.open("bgimage.jpg")
bg = ctk.CTkImage(bg_image, size=(2000, 800))
bg_label = ctk.CTkLabel(login_window, image=bg, text="")
bg_label.pack(fill="both", expand=True)

frame = ctk.CTkFrame(login_window, width=490, height=350, corner_radius=12, fg_color="#000000", bg_color="transparent")
frame.place(relx=0.5, rely=0.5, anchor='center')

ctk.CTkLabel(frame, text="Sign In", font=("Arial", 24, "bold"), text_color="white").pack(pady=(20, 10))

email_entry = ctk.CTkEntry(frame, placeholder_text="Email or phone number", width=400, height=40)
email_entry.pack(pady=10)
email_entry.bind("<FocusIn>", clear_email_placeholder)

password_entry = ctk.CTkEntry(frame, placeholder_text="Password", width=400, height=40)
password_entry.pack(pady=10)
password_entry.bind("<FocusIn>", clear_password_placeholder)

ctk.CTkButton(frame, text="Sign In", command=on_login, fg_color="red", hover_color="#770000", width=400, height=40).pack(pady=15)

remember = ctk.CTkCheckBox(frame, text="Remember me", text_color="white", checkbox_height=16, checkbox_width=16)
remember.pack(pady=(0,5))

ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10), text_color="white").pack()
ctk.CTkLabel(frame, text="This page is protected by Google reCAPTCHA", font=("Arial", 8), text_color="gray").pack()

# --- Sidebar Navigation ---
sidebar = ctk.CTkFrame(root, width=200, fg_color="#111")
sidebar.pack(side="left", fill="x")

nav_buttons = [
    ("Home", show_all),
    ("Continue Watching", show_continue_watchlist),
    ("Bollywood", lambda: show_category("Bollywood")),
    ("Hollywood", lambda: show_category("Hollywood")),
    ("Series", lambda: show_category("Series")),
    ("Anime", lambda: show_category("Anime")),
    ("Suggestions", show_suggestions),
    ("History", show_history),
]

for text, cmd in nav_buttons:
    ctk.CTkButton(sidebar, text=text, command=cmd, fg_color="#0D1D28", text_color="white", hover_color="#222", anchor="w").pack(fill="x", pady=2, padx=5)

# --- Main Frame ---
main_frame = ctk.CTkFrame(root, fg_color="#0D1D28")
main_frame.pack(side="right", fill="both", expand=True)

title_var = ctk.StringVar()
search_var = ctk.StringVar()
movies = load_movies()

input_frame = ctk.CTkFrame(main_frame, fg_color="#0D1D28")
input_frame.pack(padx=10, pady=(8, 6), fill="x")

title_entry = ctk.CTkEntry(input_frame, textvariable=title_var, width=500, placeholder_text="Movie Title")
title_entry.pack(side="left", padx=(0,8))
title_entry.bind("<Return>", add_movie)

ctk.CTkButton(input_frame, text="Add Movie", command=add_movie, fg_color="#920202", hover_color="#770000").pack(side="left", padx=(0,6))

search_frame = ctk.CTkFrame(main_frame, fg_color="#0D1D28")
search_frame.pack(fill="x", padx=10, pady=(6, 4))

search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, width=500)
search_entry.pack(side="left", padx=(0,8))
search_entry.insert(0, "🔍 Search...")
search_entry.bind("<FocusIn>", remove_search_placeholder)
search_entry.bind("<FocusOut>", add_search_placeholder)
search_var.trace_add("write", update_list)

ctk.CTkButton(search_frame, text="Clear", command=clear_search).pack(side="left")

tree = ttk.Treeview(main_frame, columns=("Title", "Category", "Watched"), show="headings", height=16)
tree.heading("Title", text="Title")
tree.column("Title", width=300)
tree.heading("Category", text="Category")
tree.column("Category", width=120)
tree.heading("Watched", text="Watched")
tree.column("Watched", width=80)
tree.pack(fill="both", expand=True, padx=10, pady=8)

btn_frame = ctk.CTkFrame(main_frame, fg_color="#0D1D28")
btn_frame.pack(pady=(0,10))

ctk.CTkButton(btn_frame, text="Mark as Watched", command=mark_watched, fg_color="#920202").pack(side="left", padx=6)
ctk.CTkButton(btn_frame, text="Delete Movie", command=delete_movie, fg_color="#920202").pack(side="left", padx=6)

# Run app
show_all()
update_list()
root.mainloop()


