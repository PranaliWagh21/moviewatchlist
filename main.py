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

# Save data
def save_movies():
    with open(FILE, "w") as f:
        json.dump(movies, f)

# Add movie
def add_movie():
    title = title_var.get().strip()
    note = note_var.get().strip()
    if title:
        movies.append({"title": title, "note": note, "watched": False})
        save_movies()
        update_list()
        title_var.set("")
        note_var.set("")
    else:
        messagebox.showwarning("Input", "Enter movie title.")

# Delete selected
def delete_movie():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        movies.pop(index)
        save_movies()
        update_list()
    else:
        messagebox.showwarning("Select", "Select movie to delete.")

# Mark as watched
def mark_watched():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        movies[index]["watched"] = True
        save_movies()
        update_list()
    else:
        messagebox.showwarning("Select", "Select movie to mark as watched.")

# Update Treeview
def update_list():
    tree.delete(*tree.get_children())
    for i, m in enumerate(movies):
        status = "✅" if m["watched"] else "❌"
        tree.insert("", "end", iid=i, values=(m["title"], m["note"], status))

# GUI setup
root = tk.Tk()
top = Toplevel()
top.title('📽️MovieMAX')
top.geometry("500x500")



pil_img = Image.open("bgimage.jpg")  # supports JPG, PNG, GIF, BMP etc.
tk_img = ImageTk.PhotoImage(pil_img)

label = tk.Label(top, image=tk_img)
label.image = tk_img  # keep a reference to prevent garbage collection
label.pack()

root.title("📽️MovieMAX")
#root.geometry("500x500")
root.configure(bg="#0D1D28")


image = Image.open("logo.jpg")  # or logo.png
resized = image.resize((150, 150))  # optional resize
logo = ImageTk.PhotoImage(resized)

# Add to label
logo_label = tk.Label(root, image=logo,bd=0)
logo_label.pack(side="top", anchor="w", padx=5,pady=5)

#w = Label(root, text='Unlimited movies,TV shows and more',font=60,fg="red",bg="#0D1D28")
#w.pack(anchor="center",pady=10,padx=10)

# Keep a reference to avoid garbage collection
logo_label.image = logo

title_var = tk.StringVar()
note_var = tk.StringVar()
movies = load_movies()


tk.Label(root, text="Movie Title:").pack()
tk.Entry(root, textvariable=title_var, width=40).pack()

tk.Label(root, text="Note (Optional):").pack()
tk.Entry(root, textvariable=note_var, width=40).pack(pady=5)

tk.Button(root, text="Add Movie", command=add_movie).pack(pady=5)

# Treeview
tree = ttk.Treeview(root, columns=("Title", "Note", "Watched"), show="headings")
tree.heading("Title", text="Title")
tree.heading("Note", text="Note")
tree.heading("Watched", text="Watched")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Button(root, text="Mark as Watched", command=mark_watched,bg="#920202",fg="white",).pack(pady=2)
tk.Button(root, text="Delete Movie", command=delete_movie,bg="#920202",fg="white",).pack(pady=2)

h_scroll = tk.Scrollbar(root, orient="horizontal", command=tree.xview)
h_scroll.pack(side="bottom", fill="x")
tree.config(xscrollcommand=h_scroll.set)

update_list()
root.mainloop()
     