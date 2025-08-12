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
        self.image_refs = []  # Keep image references here

        self.create_widgets()

    def create_widgets(self):
        # Search frame
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", padx=10, pady=10)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="🔍 Search...",
                                         textvariable=self.search_var, width=600)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.perform_search)

        self.movie_btn = ctk.CTkButton(self.search_frame, text="Movies", command=self.filter_movies)
        self.series_btn = ctk.CTkButton(self.search_frame, text="Web Series", command=self.filter_series)
        self.reset_btn = ctk.CTkButton(self.search_frame, text="All", command=self.reset_filter)

        self.movie_btn.pack(side="left", padx=5)
        self.series_btn.pack(side="left", padx=5)
        self.reset_btn.pack(side="left", padx=5)

        # Scrollable movie list
        self.display_frame = ctk.CTkScrollableFrame(self, width=900, height=600)
        self.display_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.render_movies()

    def perform_search(self, event=None):
        query = self.search_var.get().lower()
        self.filtered_data = [m for m in self.data if query in m["title"].lower()]
        self.render_movies()

    def filter_movies(self):
        self.filtered_data = [m for m in self.data if m["type"] == "Movie"]
        self.render_movies()

    def filter_series(self):
        self.filtered_data = [m for m in self.data if m["type"] == "Web Series"]
        self.render_movies()

    def reset_filter(self):
        self.filtered_data = self.data
        self.render_movies()

    def render_movies(self):
        # Clear previous widgets
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()

        for movie in self.filtered_data:
            frame = ctk.CTkFrame(self.display_frame)
            frame.pack(pady=10, padx=10, fill="x")

            # Poster
            if os.path.exists(movie["poster"]):
                img = Image.open(movie["poster"])
                photo = ctk.CTkImage(light_image=img, size=(100, 150))
                img_label = ctk.CTkLabel(frame, image=photo, text="")
                img_label.pack(side="left", padx=10)

                # Store reference so GC doesn't remove it
                self.image_refs.append(photo)
            else:
                ctk.CTkLabel(frame, text="No Image").pack(side="left", padx=10)

            # Details
            text = f"{movie['title']} ({movie['year']})\nType: {movie['type']}\n" \
                   f"Rating: {movie['rating']}\nLanguage: {movie['language']}\n" \
                   f"Genres: {', '.join(movie['genres'])}"
            detail_label = ctk.CTkLabel(frame, text=text, anchor="w", justify="left")
            detail_label.pack(side="left", padx=10)

            

            # View button
           # view_btn = ctk.CTkButton(frame, text="View Details", command=lambda m=movie: self.show_details(m))
            #view_btn.pack(side="right", padx=10)

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
    ctk.CTkLabel(login_window, image=bg, text="").pack(fill="both", expand=True)

# Login frame
frame = ctk.CTkFrame(login_window, width=490, height=350, corner_radius=12, fg_color="#000000")
frame.place(relx=0.5, rely=0.5, anchor='center')

ctk.CTkLabel(frame, text="Sign In", font=("Arial", 24, "bold"), text_color="white").pack(pady=(20, 10))

email_entry = ctk.CTkEntry(frame, placeholder_text="Email or phone number", width=400, height=40)
email_entry.pack(pady=10)
email_entry.bind("<FocusIn>", clear_email_placeholder)

password_entry = ctk.CTkEntry(frame, placeholder_text="Password", width=400, height=40)
password_entry.pack(pady=10)
password_entry.bind("<FocusIn>", clear_password_placeholder)

ctk.CTkButton(frame, text="Sign In", command=on_login, fg_color="red",
              hover_color="#770000", width=400, height=40).pack(pady=15)

ctk.CTkCheckBox(frame, text="Remember me", text_color="white").pack(pady=(0, 5))
ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10),
             text_color="white").pack()
ctk.CTkLabel(frame, text="This page is protected by Google reCAPTCHA",
             font=("Arial", 8), text_color="gray").pack()

app.mainloop()
