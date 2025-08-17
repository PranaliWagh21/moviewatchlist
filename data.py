# data.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import json
import os
import webbrowser

# ----------------- Global Login Helpers (use with Toplevel) -----------------
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
        ctk.messagebox.showwarning("Input Error", "Please enter your email or phone number.")
        return
    if password == "" or password == "Password":
        ctk.messagebox.showwarning("Input Error", "Please enter your password.")
        return
    # Close login window and show main app
    login_window.destroy()
    app.deiconify()


# ----------------- Movie App -----------------
class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎬 MovieMAX")
        self.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color="black")

        # Data + state
        self.movies_data = self.load_movies()     # dict: {"movies":[...], "series":[...]}
        self.watchlist = []                       # list of items
        self.image_refs = []                      # keep image references if you add posters later

        # ----------------- Navbar -----------------
        navbar = ctk.CTkFrame(self, height=70, fg_color="#000000", corner_radius=0)
        navbar.pack(side="top", fill="x")

        overlay = ctk.CTkFrame(navbar, fg_color="#1A1A1A")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Logo
        logo = ctk.CTkLabel(
            overlay, text="🎬 MovieMAX", font=("Arial Black", 22), text_color="red"
        )
        logo.pack(side="left", padx=20)

        # Center nav buttons
        nav_center = ctk.CTkFrame(overlay, fg_color="transparent")
        nav_center.pack(side="left", padx=80)

        nav_btns = [
            ("🏠 Home", self.show_home),
            ("🎬 Movies", self.show_movies),
            ("📺 Web Series", self.show_series),
            ("⭐ Watchlist", self.show_watchlist),
        ]
        for text, cmd in nav_btns:
            btn = ctk.CTkButton(
                nav_center,
                text=text,
                command=cmd,
                width=120,
                height=38,
                corner_radius=30,
                fg_color="#1E1E1E",
                hover_color="#FF3333",
                text_color="white",
                font=("Arial", 14, "bold"),
            )
            btn.pack(side="left", padx=10)

        # Profile (dummy)
        profile_btn = ctk.CTkButton(
            overlay,
            text="👤 Profile",
            width=100,
            height=36,
            corner_radius=20,
            fg_color="#333333",
            hover_color="#FF3333",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=self.show_home,
        )
        profile_btn.pack(side="right", padx=20)

        # ----------------- Search Bar -----------------
        search_frame = ctk.CTkFrame(self, height=60, fg_color="#1A1A1A", corner_radius=10)
        search_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search movies or series...",
            width=400,
            height=40,
            corner_radius=20,
            fg_color="#1E1E1E",
            text_color="white",
        )
        self.search_entry.pack(pady=10, padx=20, side="left")

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            height=40,
            corner_radius=20,
            fg_color="#FF3333",
            hover_color="#AA0000",
            command=self.search_movies,  # implemented below
        )
        search_btn.pack(side="left")

        # ----------------- Main Content -----------------
        self.content_frame = ctk.CTkFrame(self, fg_color="black")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Default page
        self.show_home()

    # ----------------- Data Loader -----------------
    def load_movies(self):
        """
        Loads data from data.json if present.
        Expected format:
        {
          "movies": [{"title":"Inception","trailer":"https://..."}],
          "series": [{"title":"Dark","trailer":"https://..."}]
        }
        If file missing or invalid, creates sample data.
        """
        default_data = {
            "movies": [
                {"title": "Inception", "trailer": "https://www.youtube.com/watch?v=8hP9D6kZseM"},
                {"title": "Interstellar", "trailer": "https://www.youtube.com/watch?v=zSWdZVtXT7E"},
                {"title": "Dune", "trailer": "https://www.youtube.com/watch?v=n9xhJrPXop4"},
            ],
            "series": [
                {"title": "Breaking Bad", "trailer": "https://www.youtube.com/watch?v=HhesaQXLuRY"},
                {"title": "Dark", "trailer": "https://www.youtube.com/watch?v=rrwycJ08PSA"},
                {"title": "Stranger Things", "trailer": "https://www.youtube.com/watch?v=b9EkMc79ZSU"},
            ],
        }
        try:
            if os.path.exists("data.json"):
                with open("data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Accept list or dict; normalize to dict
                if isinstance(data, list):
                    # try splitting by "type"
                    movies = [x for x in data if str(x.get("type", "")).lower() == "movie"]
                    series = [x for x in data if str(x.get("type", "")).lower() in ("series", "web series")]
                    # if not typed, put all into movies
                    if not movies and not series:
                        movies = data
                    return {"movies": movies, "series": series}
                if isinstance(data, dict):
                    return {
                        "movies": list(data.get("movies", [])),
                        "series": list(data.get("series", [])),
                    }
        except Exception as e:
            print("Failed to read data.json, using defaults. Error:", e)
        return default_data

    # ----------------- Utility -----------------
    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def add_to_watchlist(self, item):
        # avoid duplicates by title
        titles = [x.get("title") for x in self.watchlist]
        if item.get("title") not in titles:
            self.watchlist.append(item)
            messagebox.showinfo("Watchlist", f"Added: {item.get('title')}")
        else:
            messagebox.showinfo("Watchlist", f"Already in watchlist: {item.get('title')}")

    def play_trailer(self, url):
        if url:
            webbrowser.open(url)
        else:
            messagebox.showwarning("No Trailer", "Trailer URL not available.")

    # ----------------- Pages -----------------
    def show_home(self):
        self.clear_content()
        title = ctk.CTkLabel(
            self.content_frame,
            text="🏠 Welcome to MovieMAX",
            font=("Arial Black", 26),
            text_color="white",
        )
        title.pack(pady=(10, 5), anchor="w")

        sub = ctk.CTkLabel(
            self.content_frame,
            text="Browse Movies and Web Series • Use Search above",
            font=("Arial", 14),
            text_color="#bbbbbb",
        )
        sub.pack(pady=(0, 10), anchor="w")

        # quick sections
        if self.movies_data.get("movies"):
            sec = ctk.CTkLabel(self.content_frame, text="🎬 Movies", font=("Arial", 18, "bold"))
            sec.pack(anchor="w", padx=5, pady=(10, 0))
            self._create_cards(self.movies_data["movies"])

        if self.movies_data.get("series"):
            sec = ctk.CTkLabel(self.content_frame, text="📺 Web Series", font=("Arial", 18, "bold"))
            sec.pack(anchor="w", padx=5, pady=(20, 0))
            self._create_cards(self.movies_data["series"])

    def show_movies(self):
        self.clear_content()
        header = ctk.CTkLabel(self.content_frame, text="🎬 Movies", font=("Arial Black", 24))
        header.pack(pady=10, anchor="w")
        self._create_list(self.movies_data.get("movies", []))

    def show_series(self):
        self.clear_content()
        header = ctk.CTkLabel(self.content_frame, text="📺 Web Series", font=("Arial Black", 24))
        header.pack(pady=10, anchor="w")
        self._create_list(self.movies_data.get("series", []))

    def show_watchlist(self):
        self.clear_content()
        header = ctk.CTkLabel(self.content_frame, text="⭐ Your Watchlist", font=("Arial Black", 24))
        header.pack(pady=10, anchor="w")
        if not self.watchlist:
            empty = ctk.CTkLabel(self.content_frame, text="No items in watchlist.", text_color="gray")
            empty.pack(pady=20)
            return
        self._create_list(self.watchlist)

    # ----------------- Search -----------------
    def search_movies(self):
        query = self.search_entry.get().strip().lower()
        self.clear_content()

        header = ctk.CTkLabel(
            self.content_frame,
            text=f"🔍 Search Results for: {query or 'All'}",
            font=("Arial Black", 20),
        )
        header.pack(pady=10, anchor="w")

        all_items = list(self.movies_data.get("movies", [])) + list(self.movies_data.get("series", []))
        if query:
            results = [x for x in all_items if query in str(x.get("title", "")).lower()]
        else:
            results = all_items

        if not results:
            ctk.CTkLabel(self.content_frame, text="No results found.", text_color="gray").pack(pady=20)
            return

        self._create_list(results)

    # ----------------- UI Builders -----------------
    def _create_list(self, items):
        """
        Vertical list: each row title + Play + Add Watchlist
        """
        for item in items:
            frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1A1A", corner_radius=10)
            frame.pack(fill="x", padx=10, pady=8)

            title = ctk.CTkLabel(frame, text=item.get("title", "Untitled"), font=("Arial", 16, "bold"))
            title.pack(side="left", padx=15, pady=12)

            play_btn = ctk.CTkButton(
                frame, text="▶ Play", width=90, command=lambda url=item.get("trailer"): self.play_trailer(url)
            )
            play_btn.pack(side="right", padx=10)

            add_btn = ctk.CTkButton(
                frame, text="＋ Watchlist", width=120, command=lambda it=item: self.add_to_watchlist(it)
            )
            add_btn.pack(side="right", padx=10)

            

    def _create_cards(self, items):
        """
        Horizontal cards (simple): title + buttons
        """
        wrap = ctk.CTkFrame(self.content_frame, fg_color="#121212")
        wrap.pack(fill="x", padx=5, pady=5)

        for item in items:
            card = ctk.CTkFrame(wrap, fg_color="#222222", corner_radius=12)
            card.pack(side="left", padx=8, pady=8)

            title = ctk.CTkLabel(card, text=item.get("title", "Untitled"), font=("Arial", 14, "bold"))
            title.pack(padx=12, pady=(10, 6))

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(padx=10, pady=(0, 10))

            play_btn = ctk.CTkButton(
                btns, text="▶ Play Now",
                command=lambda url=item.get("trailer"): self.play_trailer(url),
                width=120
            )
            play_btn.pack(side="left", padx=5)

            add_btn = ctk.CTkButton(
                btns, text="＋ Watchlist",
                command=lambda it=item: self.add_to_watchlist(it),
                width=120
            )
            add_btn.pack(side="left", padx=5)


# ----------------- Run App with Login Toplevel -----------------
if __name__ == "__main__":
    app = MovieApp()
    app.withdraw()  # hide main window until login

    # Login Window
    login_window = ctk.CTkToplevel()
    login_window.title("LOGIN - MovieMAX")
    login_window.geometry("900x540")
    login_window.configure(fg_color="black")
    login_window.resizable(False, False)
    login_window.grab_set()

    # Optional background
    if os.path.exists("bgimage.jpg"):
        bg_image = Image.open("bgimage.jpg")
        bg = ctk.CTkImage(bg_image, size=(1600, 900))
        bg_label = ctk.CTkLabel(login_window, image=bg, text="")
        bg_label.place(relx=0.5, rely=0.5, anchor="center")

    # Overlay frame (form)
    frame = ctk.CTkFrame(login_window, width=480, height=330, corner_radius=16, fg_color="#161B22")
    frame.place(relx=0.5, rely=0.5, anchor='center')

    ctk.CTkLabel(frame, text="Sign In to MovieMAX", font=("Arial", 22, "bold"), text_color="white").pack(pady=(18, 10))

    email_entry = ctk.CTkEntry(frame, placeholder_text="Email or phone number", width=380, height=40)
    email_entry.pack(pady=10)
    email_entry.bind("<FocusIn>", clear_email_placeholder)

    password_entry = ctk.CTkEntry(frame, placeholder_text="Password", width=380, height=40)
    password_entry.pack(pady=10)
    password_entry.bind("<FocusIn>", clear_password_placeholder)

    ctk.CTkButton(frame, text="Sign In", command=on_login, fg_color="#FF0000",
                  hover_color="#770000", width=380, height=40).pack(pady=14)

    ctk.CTkCheckBox(frame, text="Remember me", text_color="white").pack(pady=(0, 5))
    ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10), text_color="white").pack()
    ctk.CTkLabel(frame, text="Protected by Google reCAPTCHA", font=("Arial", 9), text_color="gray").pack(pady=(2,0))

    app.mainloop()
