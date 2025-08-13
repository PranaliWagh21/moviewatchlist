import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import json
import os
import tkinter as tk

# ----------------- Helper Functions -----------------
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
    app.deiconify()  # Show the main app window

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return []

# ----------------- Main App Class -----------------
class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MovieMAX")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.data = load_data()
        self.filtered_data = self.data
        self.image_refs = []

        self.create_widgets()

    def create_widgets(self):
        # Navbar
        navbar = ctk.CTkFrame(self, height=55, fg_color="#0A0F13", corner_radius=0)
        navbar.pack(side="top", fill="x")

        nav_buttons = [
            ("🏠 Home", self.reset_filter),
            ("🎬 Movies", self.filter_movies),
            ("📺 Web Series", self.filter_series),
            ("🔍 Search", lambda: self.search_entry.focus())
        ]
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                navbar, text=text, command=command,
                width=140, height=35, corner_radius=20,
                fg_color="#1A1F23", hover_color="#FF0000",
                text_color="white", font=("Arial", 14, "bold")
            )
            btn.pack(side="left", padx=10, pady=10)

        # Search Bar
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=10, pady=10)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search movies & series...",
            textvariable=self.search_var,
            width=600, height=40,
            font=("Arial", 13)
        )
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.perform_search)

        # Custom display frame (replaces CTkScrollableFrame)
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.render_movies()

    def perform_search(self, event=None):
        query = self.search_var.get().lower()
        self.filtered_data = [m for m in self.data if query in m["title"].lower()]
        self.render_movies()

    def filter_movies(self):
        self.filtered_data = [m for m in self.data if m["type"].lower() == "movie"]
        self.render_movies()

    def filter_series(self):
        self.filtered_data = [m for m in self.data if m["type"].lower() == "web series"]
        self.render_movies()

    def reset_filter(self):
        self.filtered_data = self.data
        self.render_movies()

    def render_movies(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()

        # Scrollable canvas for horizontal movie layout
        canvas = tk.Canvas(self.display_frame, bg="#111111", highlightthickness=0)
        canvas.pack(side="top", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.display_frame, orient="horizontal", command=canvas.xview)
        scrollbar.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=scrollbar.set)

        container = ctk.CTkFrame(canvas, fg_color="#111111")
        canvas.create_window((0, 0), window=container, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        container.bind("<Configure>", on_configure)

        for movie in self.filtered_data:
            card = ctk.CTkFrame(container, width=180, height=360, corner_radius=12, fg_color="#1c1c1c")
            card.pack_propagate(False)
            card.pack(side="left", padx=10, pady=10)

            if os.path.exists(movie["poster"]):
                img = Image.open(movie["poster"])
                img = img.resize((160, 240))
                photo = ctk.CTkImage(light_image=img, size=(160, 240))
                self.image_refs.append(photo)
                img_label = ctk.CTkLabel(card, image=photo, text="")
                img_label.pack(pady=(10, 5))
            else:
                ctk.CTkLabel(card, text="No Image", font=("Arial", 12), text_color="gray").pack(pady=(10, 5))

            title_label = ctk.CTkLabel(
                card, text=f"{movie['title']} ({movie['year']})",
                font=("Arial", 12, "bold"), text_color="white", wraplength=160, justify="center"
            )
            title_label.pack(pady=(0, 2))

            info_text = f"⭐ {movie['rating']} | {movie['language']}\n{', '.join(movie['genres'])}"
            ctk.CTkLabel(card, text=info_text, font=("Arial", 10), text_color="#bbbbbb", justify="center").pack()

            ctk.CTkButton(
                card, text="Play Now", command=on_login,
                fg_color="#FF0000", hover_color="#770000",
                width=120, height=30
            ).pack(pady=6)

    def show_details(self, movie):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(movie["title"])
        detail_window.geometry("500x400")

        ctk.CTkLabel(detail_window, text=movie["title"], font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(detail_window, text=movie["description"], wraplength=450, justify="left").pack(pady=10)
        more = f"Type: {movie['type']}\nGenres: {', '.join(movie['genres'])}\n" \
               f"Rating: {movie['rating']}\nLanguage: {movie['language']}"
        ctk.CTkLabel(detail_window, text=more, justify="left").pack(pady=10)

# ----------------- App Setup -----------------
app = MovieApp()
app.withdraw()  # Hide until login is done

# Login Window
login_window = ctk.CTkToplevel()
login_window.title("LOGIN - MovieMAX")
login_window.geometry("1000x600")
login_window.configure(fg_color="black")

# Background image
if os.path.exists("bgimage.jpg"):
    bg_image = Image.open("bgimage.jpg")
    bg = ctk.CTkImage(bg_image, size=(2000, 800))
    bg_label = ctk.CTkLabel(login_window, image=bg, text="")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

# Semi-transparent overlay
if os.path.exists("overlay.png"):
    overlay_img = Image.open("overlay.png")
    overlay_ctk = ctk.CTkImage(light_image=overlay_img, size=(1000, 600))
    ctk.CTkLabel(login_window, image=overlay_ctk, text="").place(x=0, y=0)

# Login frame
frame = ctk.CTkFrame(login_window, width=490, height=350, corner_radius=15, fg_color="#161B22")
frame.place(relx=0.5, rely=0.5, anchor='center')

ctk.CTkLabel(frame, text="Sign In to MovieMAX", font=("Arial", 24, "bold"), text_color="white").pack(pady=(20, 10))

email_entry = ctk.CTkEntry(frame, placeholder_text="Email or phone number", width=400, height=40)
email_entry.pack(pady=10)
email_entry.bind("<FocusIn>", clear_email_placeholder)

password_entry = ctk.CTkEntry(frame, placeholder_text="Password", width=400, height=40)
password_entry.pack(pady=10)
password_entry.bind("<FocusIn>", clear_password_placeholder)

ctk.CTkButton(frame, text="Sign In", command=on_login, fg_color="#FF0000",
              hover_color="#770000", width=400, height=40).pack(pady=15)

ctk.CTkCheckBox(frame, text="Remember me", text_color="white").pack(pady=(0, 5))
ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10), text_color="white").pack()
ctk.CTkLabel(frame, text="Protected by Google reCAPTCHA", font=("Arial", 8), text_color="gray").pack()

app.mainloop()
