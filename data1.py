# data.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import webbrowser

# ---------------- Global helper placeholders (will be bound in login) ----------------
email_entry = None
password_entry = None

# ----------------- Utility functions -----------------
def load_data_file(path="data.json"):
    """Load movie/series data from JSON file. Return a list of dicts (items)."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Accept either list or dict with 'movies'/'series'
            if isinstance(data, dict):
                # normalize to list of items with 'type'
                items = []
                for t in ("movies", "series"):
                    for entry in data.get(t, []):
                        # ensure 'type' set
                        item = dict(entry)
                        if "type" not in item:
                            item["type"] = "movie" if t == "movies" else "web series"
                        items.append(item)
                return items
            elif isinstance(data, list):
                return data
        except Exception as e:
            print("Error loading data.json:", e)
    return []


# Placeholder messagebox wrappers (use tkinter.messagebox)
def safe_showinfo(title, msg):
    try:
        messagebox.showinfo(title, msg)
    except Exception:
        print(title, msg)

def safe_showwarning(title, msg):
    try:
        messagebox.showwarning(title, msg)
    except Exception:
        print(title, msg)


# ---------------- Login placeholder functions ----------------
def clear_email_placeholder(event):
    global email_entry
    try:
        if email_entry and email_entry.get() == "Email or phone number":
            email_entry.delete(0, "end")
            try:
                email_entry.configure(text_color="white")
            except Exception:
                pass
    except Exception:
        pass

def clear_password_placeholder(event):
    global password_entry
    try:
        if password_entry and password_entry.get() == "Password":
            password_entry.delete(0, "end")
            try:
                password_entry.configure(show="*", text_color="white")
            except Exception:
                password_entry.configure(show="*")
    except Exception:
        pass

def reset_email_placeholder(event):
    global email_entry
    try:
        if email_entry and email_entry.get().strip() == "":
            email_entry.insert(0, "Email or phone number")
            try:
                email_entry.configure(text_color="gray")
            except Exception:
                pass
    except Exception:
        pass

def reset_password_placeholder(event):
    global password_entry
    try:
        if password_entry and password_entry.get().strip() == "":
            password_entry.insert(0, "Password")
            try:
                password_entry.configure(show="", text_color="gray")
            except Exception:
                password_entry.configure(show="")
    except Exception:
        pass


# ----------------- Main App -----------------
class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # App window
        self.title("📽️ MovieMAX")
        self.geometry("1200x800")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color="#121212")

        # Data and state
        self.data_items = load_data_file("data.json")  # list of dicts
        # ensure each item has required keys to avoid KeyError
        for it in self.data_items:
            it.setdefault("title", "Untitled")
            it.setdefault("type", "movie")
            it.setdefault("poster", "")
            it.setdefault("year", "")
            it.setdefault("rating", "")
            it.setdefault("language", "")
            it.setdefault("genres", [])
            it.setdefault("description", "")
            it.setdefault("trailer_url", it.get("trailer") or it.get("trailer_url", ""))

        self.filtered_data = list(self.data_items)
        self.image_refs = []          # to hold CTkImage refs so they don't gc
        self.loaded_ctkimages = {}    # cache CTkImage by path
        self.watchlist = []           # user watchlist (list of items)
        self.current_filter = None

        # UI pieces that will be created in create_widgets
        self.navbar = None
        self.search_entry = None
        self.content_container = None
        self.canvas = None
        self.content_frame = None
        self.content_window = None

        # Start by making widgets and then opening login as Toplevel
        self.create_main_widgets()
        # Hide main window until login success
        self.withdraw()
        self.create_login_window()
        

        
    

    # ----------------- Main UI (keeps your original structure, adds profile button) -----------------
    def create_main_widgets(self):
        # Top navbar frame
        self.navbar = ctk.CTkFrame(self, height=70, fg_color="#0A0F13", corner_radius=0)
        self.navbar.pack(side="top", fill="x")
        

        # Left nav buttons (Home, Movies, Series)
        left_nav = ctk.CTkFrame(self.navbar, fg_color="transparent")
        left_nav.pack(side="left", padx=15)
        logo = ctk.CTkLabel(
            left_nav, text="🎬 MovieMAX", font=("Arial Black", 22), text_color="red"
        )
        logo.pack(side="left", padx=20)


        nav_buttons = [
            ("🏠 Home", self.show_home),
            ("🎬 Movies", self.show_movies_only),
            ("📺 Web Series", self.show_series_only)
        ]
        for text, cmd in nav_buttons:
            btn = ctk.CTkButton(left_nav, text=text, command=cmd,
                                width=120, height=48, corner_radius=20,
                                fg_color="#1A1F23", hover_color="#FF3333",
                                text_color="white", font=("Arial", 14, "bold"))
            btn.pack(side="left", padx=8, pady=12)

        # Spacer so profile stays right
        spacer = ctk.CTkFrame(self.navbar, fg_color="transparent")
        spacer.pack(side="left", expand=True, fill="both")

        # Profile button (right)
        profile_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        profile_frame.pack(side="right", padx=18)

        # Try to load a profile icon; fallback to text-only button if missing
        profile_icon = None
        profile_icon_path = "profile.png"  # expected in project root
        try:
            if os.path.exists(profile_icon_path):
                img = Image.open(profile_icon_path).resize((30, 30))
                profile_icon = ctk.CTkImage(Image.open(profile_icon_path), size=(30, 30))
        except Exception:
            profile_icon = None

        # Profile button: shows avatar + small dropdown when clicked
        self.profile_btn = ctk.CTkButton(profile_frame,
                                        text=" 🧑‍💻Profile",
                                        image=profile_icon,
                                        compound="left",
                                        width=130,
                                        height=38,
                                        corner_radius=18,
                                        fg_color="#B85555",
                                        hover_color="#2E2E2E",
                                        text_color="white",
                                        font=("Arial", 12, "bold"),
                                        command=self._open_profile_menu)
        self.profile_btn.pack(side="right")

        # Search frame below navbar (keeps layout similar to your original)
        search_frame = ctk.CTkFrame(self, height=60, fg_color="#121212")
        search_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.on_search_change())

        self.search_entry = ctk.CTkEntry(search_frame, 
                                        placeholder_text="🔍 Search movies or series...",
                                         textvariable=self.search_var,

                                         width=600, height=40,
                                         font=("Arial", 14),
                                         corner_radius=20,
                                         fg_color="#1A1F23",
                                         border_width=0,
                                         text_color="white")
        self.search_entry.pack(side="left", padx=20, pady=10)

        clear_btn = ctk.CTkButton(search_frame, text="🔎Search", width=36, height=36,
                                  fg_color="#FF4444", hover_color="#CC0000",
                                  command=self.clear_search)
        clear_btn.pack(side="left", padx=(8, 20), pady=10)

        # Container + Canvas for scrollable content (same structure as original)
        self.content_container = ctk.CTkFrame(self)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=15)

        self.canvas = tk.Canvas(self.content_container, bg="#121212", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(self.content_container, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        self.content_frame = ctk.CTkFrame(self.canvas, fg_color="#121212")
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind("<Configure>", self.on_content_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.bind_all("<MouseWheel>", self.on_mousewheel)

    # ----------------- Profile Menu / Window -----------------
    def _open_profile_menu(self):
        """Open a small dropdown menu anchored to the profile button location."""
        try:
            menu = tk.Menu(self, tearoff=0, bg="#222222", fg="white", activebackground="#333333", activeforeground="white")
            menu.add_command(label="👤 My Profile", command=self.open_profile_window)
            menu.add_command(label="⭐ My Watchlist", command=self.show_watchlist)
            menu.add_command(label="⚙ Settings", command=self.open_settings_window)
            menu.add_separator()
            menu.add_command(label="🚪 Logout", command=self._logout)
            # position near mouse pointer / button
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def open_profile_window(self):
        """Open a CTkToplevel with profile details."""
        prof = ctk.CTkToplevel(self)
        prof.title("My Profile")
        prof.geometry("420x320")
        prof.configure(fg_color="#1a1a1a")
        prof.grab_set()

        # Avatar
        avatar_path = "profile.png"
        if os.path.exists(avatar_path):
            try:
                pil_img = Image.open(avatar_path).resize((90, 90))
                avatar_img = ctk.CTkImage(pil_img, size=(90, 90))
                ctk.CTkLabel(prof, image=avatar_img, text="").pack(pady=(20, 8))
                # keep reference
                prof._avatar_ref = avatar_img
            except Exception:
                pass

        ctk.CTkLabel(prof, text="Demo User", font=("Arial", 18, "bold"), text_color="white").pack(pady=(4, 2))
        ctk.CTkLabel(prof, text="demo@example.com", font=("Arial", 12), text_color="#bbbbbb").pack(pady=(0, 10))

        # Watchlist / Settings / Close
        btn_frame = ctk.CTkFrame(prof, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="My Watchlist", width=140, command=self.show_watchlist).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Settings", width=120, command=self.open_settings_window).pack(side="left", padx=8)

        ctk.CTkButton(prof, text="Logout", fg_color="#FF3333", hover_color="#CC0000", command=self._logout).pack(pady=18)

    def open_settings_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("480x300")
        win.configure(fg_color="#1a1a1a")
        win.grab_set()

        ctk.CTkLabel(win, text="Settings", font=("Arial", 18, "bold"), text_color="white").pack(pady=16)
        ctk.CTkLabel(win, text="(No settings available in demo)", text_color="#bbbbbb").pack(pady=8)
        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=18)

    def _logout(self):
        """Logout: hide main window and show login again."""
        # destroy any modal popups etc then show login
        try:
            # clear watchlist or other user-specific state if needed
            # self.watchlist.clear()
            pass
        finally:
            # Show login Toplevel again
            self.deiconify()  # ensure main exists
            # close any profile windows handled by menu actions
            self.create_login_window()

    # ----------------- Login window (Toplevel) -----------------
    def create_login_window(self):
        """Create a new modal login window (Toplevel)."""
        # if a login window already exists, avoid duplicating
        self.login_win = ctk.CTkToplevel(self)
        self.login_win.title("LOGIN - MovieMAX")
        self.login_win.geometry("1000x600")
        self.login_win.configure(fg_color="black")
        self.login_win.grab_set()

        # Optional background
        if os.path.exists("bgimage.jpg"):
            try:
                bg_image = Image.open("bgimage.jpg")
                bg = ctk.CTkImage(bg_image, size=(1600, 900))
                bg_label = ctk.CTkLabel(self.login_win, image=bg, text="")
                bg_label.place(relx=0.5, rely=0.5, anchor="center")
                # store reference to avoid GC
                self.login_win._bg_img = bg
            except Exception:
                pass

        # Login frame
        frame = ctk.CTkFrame(self.login_win, width=490, height=350, corner_radius=15, fg_color="#161B22")
        frame.place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(frame, text="Sign In to MovieMAX", font=("Arial", 24, "bold"), text_color="white").pack(pady=(18, 10))

        global email_entry, password_entry
        email_entry = ctk.CTkEntry(frame, placeholder_text="Email or phone number", width=400, height=40)
        email_entry.pack(pady=10)
        email_entry.bind("<FocusIn>", clear_email_placeholder)
        email_entry.bind("<FocusOut>", reset_email_placeholder)

        password_entry = ctk.CTkEntry(frame, placeholder_text="Password", width=400, height=40)
        password_entry.pack(pady=10)
        password_entry.bind("<FocusIn>", clear_password_placeholder)
        password_entry.bind("<FocusOut>", reset_password_placeholder)

        ctk.CTkButton(frame, text="Sign In", command=self._on_login_click, fg_color="#FF0000",
                      hover_color="#770000", width=400, height=40).pack(pady=14)

        ctk.CTkCheckBox(frame, text="Remember me", text_color="white").pack(pady=(0, 6))
        ctk.CTkLabel(frame, text="New to MovieMAX? Sign up now", font=("Arial", 10), text_color="white").pack()
        ctk.CTkLabel(frame, text="Protected by Google reCAPTCHA", font=("Arial", 8), text_color="gray").pack(pady=(2, 0))

    def _on_login_click(self):
        """Validate login fields and on success close login window and show main."""
        global email_entry, password_entry
        if not email_entry or not password_entry:
            safe_showwarning("Input Error", "Login fields missing.")
            return
        email = email_entry.get().strip()
        pwd = password_entry.get().strip()
        if email == "" or email == "Email or phone number":
            safe_showwarning("Input Error", "Please enter your email or phone number.")
            return
        if pwd == "" or pwd == "Password":
            safe_showwarning("Input Error", "Please enter your password.")
            return
        # For demo purposes we accept any non-empty credentials
        try:
            # close login window then show main window
            if hasattr(self, "login_win") and self.login_win.winfo_exists():
                self.login_win.destroy()
        except Exception:
            pass
        self.deiconify()
        # show home content
        self.show_home()

    # ----------------- Content management -----------------
    def clear_content_area(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        self.image_refs.clear()

    def show_home(self):
        """Show main homepage with movie and series sections (grid)."""
        self.current_filter = None
        # reset search field if present
        try:
            if self.search_entry:
                self.search_entry.delete(0, "end")
        except Exception:
            pass
        self.filtered_data = list(self.data_items)
        self.populate_home_sections()

    def show_movies_only(self):
        self.current_filter = "movie"
        self.filtered_data = [m for m in self.data_items if str(m.get("type", "")).lower() == "movie"]
        self.populate_grid(self.filtered_data, "Movies")

    def show_series_only(self):
        self.current_filter = "web series"
        self.filtered_data = [m for m in self.data_items if "series" in str(m.get("type", "")).lower()]
        self.populate_grid(self.filtered_data, "Web Series")

    def populate_home_sections(self):
        """Create two big sections: Movies and Web Series — use grid layout similar to earlier code."""
        self.clear_content_area()

        movies = [m for m in self.data_items if str(m.get("type", "")).lower() == "movie"]
        series = [m for m in self.data_items if "series" in str(m.get("type", "")).lower()]

        def add_section(title, items, start_row):
            if not items:
                return start_row
            lbl = ctk.CTkLabel(self.content_frame, text=title, font=("Arial", 26, "bold"), text_color="white")
            lbl.grid(row=start_row, column=0, sticky="w", pady=(18, 8), padx=10, columnspan=7)
            start_row += 1

            cols = 7
            col_num = 0

            for col in range(cols):
                self.content_frame.grid_columnconfigure(col, weight=1, uniform="col")

            for item in items:
                card = ctk.CTkFrame(self.content_frame, fg_color="#222222", corner_radius=12)
                card.grid(row=start_row, column=col_num, padx=8, pady=8, sticky="nsew")

                # poster
                poster_path = item.get("poster", "")
                if poster_path and os.path.exists(poster_path):
                    try:
                        pil_img = Image.open(poster_path).resize((160, 250))
                        ctk_img = ctk.CTkImage(pil_img, size=(160, 250))
                        lbl_img = ctk.CTkLabel(card, image=ctk_img, text="")
                        lbl_img.pack(pady=(10, 6))
                        # keep reference
                        self.image_refs.append(ctk_img)
                    except Exception:
                        ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)
                else:
                    ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)

                # title and info
                ctk.CTkLabel(card, text=item.get("title", "Untitled"), font=("Arial", 14, "bold"), text_color="white",
                             wraplength=160, justify="center").pack(pady=(4, 6))
                info_txt = f"{item.get('year','')} | ⭐ {item.get('rating','')} | {item.get('language','')}"
                ctk.CTkLabel(card, text=info_txt, font=("Arial", 11), text_color="#bbbbbb").pack()

                genres_txt = ", ".join(item.get("genres", []))
                ctk.CTkLabel(card, text=genres_txt, font=("Arial", 10), text_color="#999999",
                             wraplength=160, justify="center").pack(pady=(3, 6))

                desc = item.get("description", "No description available.")
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                ctk.CTkLabel(card, text=desc, font=("Arial", 11), text_color="#dddddd",
                             wraplength=160, justify="left").pack(padx=8, pady=(0, 8))

                # bottom buttons: play + watchlist
                btns = ctk.CTkFrame(card, fg_color="transparent")
                btns.pack(pady=(4, 10))
                play_btn = ctk.CTkButton(btns, text="▶ Play Now", width=45, height=34, fg_color="#e50914",
                                         hover_color="#b20710", corner_radius=16,
                                         font=("Arial", 12, "bold"),
                                         command=lambda i=item: self.show_trailer_window(i))
                play_btn.pack(side="left", padx=4)

                wl_btn = ctk.CTkButton(btns, text=" ➕Watchlist", width=50, height=34, fg_color="#2b2b2b",
                                       hover_color="#3b3b3b", corner_radius=16,
                                       font=("Arial", 12), command=lambda it=item: self.toggle_watchlist(it))
                wl_btn.pack(side="left", padx=4)

                col_num += 1
                if col_num >= cols:
                    col_num = 0
                    start_row += 1
            return start_row + 1

        r = 0
        r = add_section("Movies", movies, r)
        r = add_section("Web Series", series, r)

    def populate_grid(self, items, title):
        """Populate a grid view for a list of items (used for lists like movies or search)."""
        self.clear_content_area()
        lbl = ctk.CTkLabel(self.content_frame, text=title, font=("Arial", 26, "bold"), text_color="white")
        lbl.grid(row=0, column=0, sticky="w", pady=(20, 8), padx=10, columnspan=7)

        cols = 7
        row = 1
        col_num = 0
        for col in range(cols):
            self.content_frame.grid_columnconfigure(col, weight=1, uniform="col")

        for item in items:
            card = ctk.CTkFrame(self.content_frame, fg_color="#222222", corner_radius=12)
            card.grid(row=row, column=col_num, padx=8, pady=8, sticky="nsew")

            poster_path = item.get("poster", "")
            if poster_path and os.path.exists(poster_path):
                try:
                    pil_img = Image.open(poster_path).resize((160, 250))
                    ctk_img = ctk.CTkImage(pil_img, size=(160, 250))
                    lbl_img = ctk.CTkLabel(card, image=ctk_img, text="")
                    lbl_img.pack(pady=(10, 6))
                    self.image_refs.append(ctk_img)
                except Exception:
                    ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)
            else:
                ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)

            ctk.CTkLabel(card, text=item.get("title", "Untitled"), font=("Arial", 14, "bold"), text_color="white",
                         wraplength=160, justify="center").pack(pady=(6, 6))
            info_txt = f"{item.get('year','')} | ⭐ {item.get('rating','')} | {item.get('language','')}"
            ctk.CTkLabel(card, text=info_txt, font=("Arial", 11), text_color="#bbbbbb").pack()

            genres_txt = ", ".join(item.get("genres", []))
            ctk.CTkLabel(card, text=genres_txt, font=("Arial", 10), text_color="#999999",
                         wraplength=160, justify="center").pack(pady=(3, 6))

            desc = item.get("description", "No description available.")
            if len(desc) > 100:
                desc = desc[:97] + "..."
            ctk.CTkLabel(card, text=desc, font=("Arial", 11), text_color="#dddddd",
                         wraplength=160, justify="left").pack(padx=8, pady=(0, 8))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(4, 8))
            play_btn = ctk.CTkButton(btn_frame, text="▶ Play Now", width=120, height=34, fg_color="#e50914",
                                     hover_color="#b20710", corner_radius=16,
                                     font=("Arial", 12, "bold"),
                                     command=lambda i=item: self.show_trailer_window(i))
            play_btn.pack(side="left", padx=6)

            wl_btn = ctk.CTkButton(btn_frame, text="＋ Watchlist", width=120, height=34, fg_color="#2b2b2b",
                                   hover_color="#3b3b3b", corner_radius=16,
                                   font=("Arial", 12), command=lambda it=item: self.toggle_watchlist(it))
            wl_btn.pack(side="left", padx=6)

            col_num += 1
            if col_num >= cols:
                col_num = 0
                row += 1

    # ----------------- Watchlist -----------------
    def toggle_watchlist(self, item):
        titles = [x.get("title") for x in self.watchlist]
        if item.get("title") in titles:
            # remove
            self.watchlist = [x for x in self.watchlist if x.get("title") != item.get("title")]
            safe_showinfo("Watchlist", f"Removed from watchlist: {item.get('title')}")
        else:
            self.watchlist.append(item)
            safe_showinfo("Watchlist", f"Added to watchlist: {item.get('title')}")

    def show_watchlist(self):
        if not self.watchlist:
            self.clear_content_area()
            ctk.CTkLabel(self.content_frame, text="⭐ Your Watchlist is empty", font=("Arial", 20), text_color="gray").pack(pady=30)
            return
        self.populate_grid(self.watchlist, "⭐ Your Watchlist")

    # ----------------- Search -----------------
    def on_search_change(self):
        query = self.search_var.get().strip().lower()
        if query == "":
            self.show_home()
        else:
            self.filtered_data = [m for m in self.data_items if query in str(m.get("title","")).lower()]
            self.populate_grid(self.filtered_data, f"Search Results for '{query}'")

    def clear_search(self):
        try:
            self.search_var.set("")
        except Exception:
            if self.search_entry:
                try:
                    self.search_entry.delete(0, "end")
                except Exception:
                    pass
        self.show_home()

    # ----------------- Trailer / Details popup -----------------
    def show_trailer_window(self, movie):
        try:
            trailer_win = ctk.CTkToplevel(self)
            trailer_win.geometry("900x520")
            trailer_win.title(f"Details - {movie.get('title','Details')}")
            trailer_win.configure(fg_color="#1c1c1c")
            trailer_win.grab_set()  # Modal window

            # Left frame for poster image
            left_frame = ctk.CTkFrame(trailer_win, width=400, height=500, fg_color="#121212")
            left_frame.pack(side="left", padx=20, pady=20)
            left_frame.pack_propagate(False)

            if movie.get("poster") and os.path.exists(movie.get("poster")):
                try:
                    img = Image.open(movie["poster"]).resize((330, 480))
                    photo = ctk.CTkImage(img, size=(330, 480))
                    lbl_img = ctk.CTkLabel(left_frame, image=photo, text="")
                    lbl_img.image = photo  # keep reference
                    lbl_img.pack(pady=10)
                except Exception:
                    ctk.CTkLabel(left_frame, text="No Image Available", font=("Arial", 16), text_color="gray").pack(pady=20)
            else:
                ctk.CTkLabel(left_frame, text="No Image Available", font=("Arial", 16), text_color="gray").pack(pady=20)

            # Right frame for details
            right_frame = ctk.CTkFrame(trailer_win, fg_color="#222222", corner_radius=12)
            right_frame.pack(side="left", fill="both", expand=True, pady=20, padx=(0,20))
            right_frame.grid_rowconfigure(2, weight=1)  # Make description expand

            # Title & info
            ctk.CTkLabel(right_frame, text=movie.get("title", ""), font=("Arial", 26, "bold"), text_color="white").grid(row=0, column=0, sticky="w", padx=20, pady=(20,8))
            info_text = (
                f"Year: {movie.get('year','N/A')}\n"
                f"Rating: ⭐ {movie.get('rating','N/A')}\n"
                f"Language: {movie.get('language','N/A')}\n"
                f"Genres: {', '.join(movie.get('genres', []))}"
            )
            ctk.CTkLabel(right_frame, text=info_text, font=("Arial", 13), text_color="#cccccc", justify="left").grid(row=1, column=0, sticky="w", padx=20, pady=(0,10))

            # Description (scrollable)
            desc_frame = ctk.CTkFrame(right_frame, fg_color="#333333", corner_radius=10)
            desc_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
            desc_text = tk.Text(desc_frame, wrap="word", font=("Arial", 13), bg="#333333", fg="white", bd=0, padx=12, pady=12)
            desc_text.insert("1.0", movie.get("description", "No description available."))
            desc_text.configure(state="disabled")
            desc_text.pack(side="left", fill="both", expand=True)
            desc_scroll = tk.Scrollbar(desc_frame, command=desc_text.yview)
            desc_scroll.pack(side="right", fill="y")
            desc_text.configure(yscrollcommand=desc_scroll.set)

            # Buttons
            btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            btn_frame.grid(row=3, column=0, sticky="e", padx=20, pady=10)

            def open_trailer():
                url = movie.get("trailer_url") or movie.get("trailer") or movie.get("url")
                if url:
                    webbrowser.open(url)
                else:
                    ctk.CTkLabel(right_frame, text="Trailer URL not available.", font=("Arial", 12), text_color="red").grid(row=4, column=0, sticky="w", padx=20)

            play_btn = ctk.CTkButton(btn_frame, text="▶ Play Now", width=160, height=42,
                                     fg_color="#e50914", hover_color="#b20710",
                                     corner_radius=20, font=("Arial", 14, "bold"),
                                     command=open_trailer)
            play_btn.pack(side="left", padx=(0,15))

            add_watch_btn = ctk.CTkButton(btn_frame, text="＋ Watchlist", width=140, height=42, command=lambda it=movie: self.toggle_watchlist(it))
            add_watch_btn.pack(side="left", padx=(0,10))

            close_btn = ctk.CTkButton(btn_frame, text="GO Back", width=100, height=42,
                                      fg_color="#FF4444", hover_color="#cc0000",
                                      command=trailer_win.destroy)
            close_btn.pack(side="left")

        except Exception as e:
            print("Error opening trailer window:", e)

    # ----------------- Scrolling helpers -----------------
    def on_content_configure(self, event):
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfigure(self.content_window, width=self.canvas.winfo_width())
        except Exception:
            pass

    def on_canvas_configure(self, event):
        try:
            self.canvas.itemconfigure(self.content_window, width=event.width)
        except Exception:
            pass

    def on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


# ----------------- Run App -----------------
if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()
