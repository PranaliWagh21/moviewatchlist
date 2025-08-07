import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json, os

FILE = "movies.json"

# Load data
def load_movies():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_movies():
    with open(FILE, "w") as f:
        json.dump(movies, f, indent=2)

# ---------------------
# Movie operations
# ---------------------
def add_movie(event=None):
    title = title_var.get().strip()
    if title:
        movies.append({"title": title, "category": "", "watched": False})
        save_movies()
        title_var.set("")
        update_list()
    else:
        messagebox.showwarning("Input", "Enter movie title.")

def delete_movie():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        if 0 <= index < len(movies):
            movies.pop(index)
            save_movies()
            update_list()
        else:
            messagebox.showerror("Error", "Selection index out of range.")
    else:
        messagebox.showwarning("Select", "Select a movie to delete.")

def mark_watched():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        if 0 <= index < len(movies):
            movies[index]["watched"] = True
            save_movies()
            update_list()
        else:
            messagebox.showerror("Error", "Selection index out of range.")
    else:
        messagebox.showwarning("Select", "Select a movie to mark as watched.")

# ---------------------
# Filtering
# ---------------------
current_filter = None

def apply_filter(filter_fn=None):
    global current_filter
    current_filter = filter_fn
    update_list()

def show_all():
    apply_filter(None)

def show_continue_watchlist():
    apply_filter(lambda m: not m.get("watched", False))

def show_history():
    apply_filter(lambda m: m.get("watched", False))

def show_suggestions():
    apply_filter(lambda m: not m.get("watched", False))

def show_category(cat_name):
    apply_filter(lambda m: m.get("category", "").lower() == cat_name.lower())

# ---------------------
# UI update
# ---------------------
def update_list(*args):
    filter_text = search_var.get().strip().lower()
    tree.delete(*tree.get_children())
    for i, m in enumerate(movies):
        title = m.get("title", "")
        category = m.get("category", "")
        watched = m.get("watched", False)
        if current_filter and not current_filter(m):
            continue
        if filter_text and filter_text not in title.lower() and filter_text not in category.lower():
            continue
        status = "✅" if watched else "❌"
        tree.insert("", "end", iid=i, values=(title, category, status))

def clear_search():
    search_var.set("")
    update_list()

# ---------------------
# Placeholder behavior
# ---------------------
def add_search_placeholder(event=None):
    if not search_var.get():
        search_entry.delete(0, tk.END)
        search_entry.insert(0, "🔍 Search...")
        search_entry.config(fg="gray")

def remove_search_placeholder(event=None):
    if search_entry.get() == "🔍 Search...":
        search_entry.delete(0, tk.END)
        search_entry.config(fg="black")

# ---------------------
# Placeholder clear for login fields
# ---------------------
def clear_email_placeholder(event):
    if email_entry.get() == "Email or phone number":
        email_entry.delete(0, tk.END)
        email_entry.config(fg="white")

def clear_password_placeholder(event):
    if password_entry.get() == "Password":
        password_entry.delete(0, tk.END)
        password_entry.config(show="*", fg="white")

# GUI setup
root = tk.Tk()
root.title("MovieMAX")
root.configure(bg="#0D1D28")

# --- Login Window ---
top = Toplevel()
top.title("LOGIN - MovieMAX")

bg_image = Image.open("bgimage.jpg")
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = Label(top, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
top.bg_img = bg_photo

canvas = tk.Canvas(top, width=1000, height=500)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=top.bg_img, anchor="nw")
canvas.create_text(800, 150,
                   text=" Welcome to MovieMAX !🎬 Unlimited movies ,\nTV shows and more🍿",
                   fill="White", font=("Arial", 40, "bold"),
                   justify="center", anchor="center")

# Semi-transparent black box
frame = Frame(top, bg='#000000', bd=0)
frame.place(relx=0.5, rely=0.5, anchor='center', width=490, height=350)

title = Label(frame, text="Sign In", fg="white", bg="#000000", font=("Arial", 24, "bold"))
title.pack(pady=(20, 10))

email_entry = Entry(frame, font=("Arial", 14), bg="#333333", fg="gray", insertbackground='white')
email_entry.insert(0, "Email or phone number")
email_entry.pack(pady=10, ipady=8, ipadx=5, fill="x", padx=40)
email_entry.bind("<FocusIn>", clear_email_placeholder)

password_entry = Entry(frame, font=("Arial", 14), bg="#333333", fg="gray", insertbackground='white')
password_entry.insert(0, "Password")
password_entry.pack(pady=10, ipady=8, ipadx=5, fill="x", padx=40)
password_entry.bind("<FocusIn>", clear_password_placeholder)

# --- Login Button Action ---
def on_login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if email == "" or email == "Email or phone number":
        messagebox.showwarning("Input Error", "Please enter your email or phone number.")
        return
    if password == "" or password == "Password":
        messagebox.showwarning("Input Error", "Please enter your password.")
        return

    top.destroy()
    root.deiconify()

sign_in_btn = Button(frame, text="Sign In", bg="red", fg="white", font=("Arial", 14, "bold"),
                     relief="flat", command=on_login)
sign_in_btn.pack(pady=20, ipadx=5, ipady=8, fill="x", padx=40)

bottom_frame = Frame(frame, bg="#000000")
bottom_frame.pack(pady=(0, 5), fill="x", padx=40)

remember = Checkbutton(bottom_frame, text="Remember me", bg="#000000", fg="white", font=("Arial", 10),
                       activebackground="#000000", activeforeground="white", selectcolor="black")
remember.pack(side=LEFT)

help_label = Label(bottom_frame, text="Need help?", fg="white", bg="#000000", font=("Arial", 10))
help_label.pack(side=RIGHT)

signup_label = Label(frame, text="New to MovieMAX? Sign up now", bg="#000000", fg="white", font=("Arial", 10))
signup_label.pack(pady=(10, 5))

info_label = Label(frame, text="This page is protected by Google reCAPTCHA to ensure you're not a bot.",
                   bg="#000000", fg="gray", font=("Arial", 8), wraplength=300, justify="center")
info_label.pack(pady=(5, 0))

# --- Main App Content ---
root.withdraw()

image = Image.open("logo.jpg")
resized = image.resize((150, 150))
logo = ImageTk.PhotoImage(resized)

logo_label = tk.Label(root, image=logo, bd=0)
logo_label.pack(side="top", anchor="w", padx=5, pady=5)
logo_label.image = logo

# 🔄 Horizontal Navigation Bar
topbar = tk.Frame(root, bg="#111")
topbar.pack(side="top", fill="x")

main_frame = tk.Frame(root, bg="#0D1D28")
main_frame.pack(side="top", fill="both", expand=True)

nav_buttons = [
    ("Home", show_all),
    ("Continue Watching", show_continue_watchlist),
    ("Bollywood", lambda: show_category("Bollywood")),
    ("Hollywood", lambda: show_category("Hindi")),
    ("Tollywood", lambda: show_category("south")),
    ("Marathi Movies", lambda: show_category("Marathi")),
    ("Series", lambda: show_category("Series")),
    ("Anime", lambda: show_category("Anime")),
    ("TV shows", lambda: show_category("Hindi")),
    ("Suggestions", show_suggestions),
    ("History", show_history),
]

for text, cmd in nav_buttons:
    btn = tk.Button(topbar, text=text, command=cmd, bg="#0D1D28", fg="white", relief="flat", padx=20, pady=9)
    btn.pack(side="left", padx=1, pady=1)

title_var = tk.StringVar()
search_var = tk.StringVar()
movies = load_movies()

input_frame = tk.Frame(main_frame, bg="#0D1D28")
input_frame.pack(padx=10, pady=(8, 6), fill="x")

title_entry = tk.Entry(input_frame, textvariable=title_var, width=45)
title_entry.pack(side="left", padx=(0,8))
title_entry.focus_set()
title_entry.bind("<Return>", add_movie)

tk.Button(input_frame, text="Add Movie", command=add_movie, bg="#920202", fg="white").pack(side="left", padx=(0,6))

search_frame = tk.Frame(main_frame, bg="#0D1D28")
search_frame.pack(fill="x", padx=10, pady=(6, 4))

search_entry = tk.Entry(search_frame, textvariable=search_var, width=45, fg="gray")
search_entry.pack(side="left", padx=(0,8))
search_entry.insert(0, "🔍 Search...")
search_entry.bind("<FocusIn>", remove_search_placeholder)
search_entry.bind("<FocusOut>", add_search_placeholder)
search_var.trace_add("write", update_list)

tk.Button(search_frame, text="Clear", command=clear_search).pack(side="left")

tree = ttk.Treeview(main_frame, columns=("Title", "Category", "Watched"), show="headings", height=16)
tree.heading("Title", text="Title")
tree.column("Title", width=300)
tree.heading("Category", text="Category")
tree.column("Category", width=120)
tree.heading("Watched", text="Watched")
tree.column("Watched", width=80)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

btn_frame = tk.Frame(main_frame, bg="#0D1D28")
btn_frame.pack(pady=(0,10))
tk.Button(btn_frame, text="Mark as Watched", command=mark_watched, bg="#920202", fg="white").pack(side="left", padx=6)
tk.Button(btn_frame, text="Delete Movie", command=delete_movie, bg="#920202", fg="white").pack(side="left", padx=6)

h_scroll = tk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
h_scroll.pack(side="bottom", fill="x")
tree.config(xscrollcommand=h_scroll.set)

# Show all movies on load
show_all()
update_list()

# Start the application
root.mainloop()
