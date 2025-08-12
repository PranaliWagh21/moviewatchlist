import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import json
import os

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

        # Movie List
        self.display_frame = ctk.CTkScrollableFrame(self, width=900, height=600)
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

        for movie in self.filtered_data:
            frame = ctk.CTkFrame(self.display_frame, corner_radius=12, fg_color="#161B22")
            frame.pack(pady=8, padx=10, fill="x")

            if os.path.exists(movie["poster"]):
                img = Image.open(movie["poster"])
                photo = ctk.CTkImage(light_image=img, size=(100, 150))
                img_label = ctk.CTkLabel(frame, image=photo, text="")
                img_label.pack(side="left", padx=10, pady=10)
                self.image_refs.append(photo)
            else:
                ctk.CTkLabel(frame, text="No Image", font=("Arial", 12), text_color="gray").pack(side="left", padx=10)

            details_frame = ctk.CTkFrame(frame, fg_color="transparent")
            details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

            title_label = ctk.CTkLabel(
                details_frame,
                text=f"{movie['title']} ({movie['year']})",
                font=("Arial", 18, "bold"),
                anchor="w"
            )
            title_label.pack(anchor="w")

            info_text = f"Type: {movie['type']}\nRating: {movie['rating']}\n" \
                        f"Language: {movie['language']}\nGenres: {', '.join(movie['genres'])}"
            ctk.CTkLabel(details_frame, text=info_text, anchor="w", justify="left", text_color="#BBBBBB").pack(anchor="w", pady=(5, 0))

            view_btn = ctk.CTkButton(details_frame, text="Play Now",
                                     command=lambda m=movie: self.show_details(m),
                                     width=140, height=35,
                                     fg_color="#FF0000", hover_color="#770000")
            view_btn.pack(anchor="w", pady=(10, 0))

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

# Semi-transparent overlay using PNG
if os.path.exists("overlay.png"):  # Make a PNG with black + 40% opacity
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
ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10),
             text_color="white").pack()
ctk.CTkLabel(frame, text="Protected by Google reCAPTCHA",
             font=("Arial", 8), text_color="gray").pack()

app.mainloop()
