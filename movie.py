import customtkinter as ctk
import tkinter as tk
from PIL import Image
import json
import os
import webbrowser

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

    login_window.destroy()
    app.deiconify()  # Show the main app window

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return []

class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📽️MovieMAX")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.data = load_data()
        self.filtered_data = self.data.copy()
        self.image_refs = []

        self.current_filter = None

        self.create_widgets()
        self.show_home()

    def create_widgets(self):
        navbar = ctk.CTkFrame(self, height=55, fg_color="#0A0F13", corner_radius=0)
        navbar.pack(side="top", fill="x")

        nav_buttons = [
            ("🏠 Home", self.show_home),
            ("🎬 Movies", self.show_movies_only),
            ("📺 Web Series", self.show_series_only),
        ]
        for text, cmd in nav_buttons:
            btn = ctk.CTkButton(navbar, text=text, command=cmd,
                                width=120, height=38, corner_radius=20,
                                fg_color="#1A1F23", hover_color="#FF3333",
                                text_color="white", font=("Arial", 14, "bold"))
            btn.pack(side="left", padx=12, pady=8)

        search_frame = ctk.CTkFrame(self, height=60, fg_color="#121212")
        search_frame.pack(fill="x", padx=20, pady=(10,0))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search movies & series...",
                                         textvariable=self.search_var,
                                         width=600, height=40,
                                         font=("Arial", 14),
                                         corner_radius=20,
                                         fg_color="#1A1F23",
                                         border_width=0,
                                         text_color="white")
        self.search_entry.pack(side="left", padx=20, pady=10)

        self.clear_btn = ctk.CTkButton(search_frame, text="✕", width=30, height=30,
                                      fg_color="#FF4444", hover_color="#CC0000",
                                      command=self.clear_search)
        self.clear_btn.pack(side="left", pady=12, padx=(5, 20))

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=15)

        self.canvas = tk.Canvas(container, bg="#121212", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        self.content_frame = ctk.CTkFrame(self.canvas, fg_color="#121212")
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind("<Configure>", self.on_content_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.bind_all("<MouseWheel>", self.on_mousewheel)

    def clear_search(self):
        self.search_var.set("")
        self.show_home()

    def on_search_change(self, *args):
        query = self.search_var.get().strip().lower()
        if query == "":
            self.show_home()
        else:
            self.filtered_data = [m for m in self.data if query in m["title"].lower()]
            self.populate_grid(self.filtered_data, "Search Results")

    def show_home(self):
        self.current_filter = None
        self.search_var.set("")
        self.filtered_data = self.data.copy()
        self.populate_home_sections()

    def show_movies_only(self):
        self.current_filter = "movie"
        self.search_var.set("")
        movies = [m for m in self.data if m["type"].lower() == "movie"]
        self.populate_grid(movies, "Movies")

    def show_series_only(self):
        self.current_filter = "web series"
        self.search_var.set("")
        series = [m for m in self.data if m["type"].lower() == "web series"]
        self.populate_grid(series, "Web Series")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()

    def populate_home_sections(self):
        self.clear_content()
        movies = [m for m in self.data if m["type"].lower() == "movie"]
        series = [m for m in self.data if m["type"].lower() == "web series"]

        def add_section(title, items, start_row):
            if not items:
                return start_row
            lbl = ctk.CTkLabel(self.content_frame, text=title, font=("Arial", 26, "bold"), text_color="white")
            lbl.grid(row=start_row, column=0, sticky="w", pady=(20, 10), padx=10, columnspan=7)
            start_row += 1

            cols = 7
            col_num = 0

            for col in range(cols):
                self.content_frame.grid_columnconfigure(col, weight=1, uniform="col")

            for item in items:
                card = ctk.CTkFrame(self.content_frame, fg_color="#222222", corner_radius=15)
                card.grid(row=start_row, column=col_num, padx=8, pady=8, sticky="nsew")

                if os.path.exists(item["poster"]):
                    img = Image.open(item["poster"]).resize((160, 250))
                    photo = ctk.CTkImage(light_image=img, size=(160, 250))
                    self.image_refs.append(photo)
                    lbl_img = ctk.CTkLabel(card, image=photo, text="")
                    lbl_img.pack(pady=(10, 5))
                else:
                    ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)

                ctk.CTkLabel(card, text=item["title"], font=("Arial", 14, "bold"), text_color="white",
                             wraplength=160, justify="center").pack(pady=(0, 5))

                info_txt = f"{item['year']} | ⭐ {item['rating']} | {item['language']}"
                ctk.CTkLabel(card, text=info_txt, font=("Arial", 11), text_color="#bbbbbb").pack()

                genres_txt = ", ".join(item["genres"])
                ctk.CTkLabel(card, text=genres_txt, font=("Arial", 10), text_color="#999999",
                             wraplength=160, justify="center").pack(pady=(3, 7))

                desc = item.get("description", "No description available.")
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                ctk.CTkLabel(card, text=desc, font=("Arial", 11), text_color="#dddddd",
                             wraplength=160, justify="left").pack(padx=8, pady=(0, 10))

                play_btn = ctk.CTkButton(card, text="▶ Play Now", width=140, height=35, fg_color="#e50914",
                                         hover_color="#b20710", corner_radius=20,
                                         font=("Arial", 13, "bold"),
                                         command=lambda i=item: self.show_trailer_window(i))
                play_btn.pack(pady=(5, 10))

                col_num += 1
                if col_num >= cols:
                    col_num = 0
                    start_row += 1
            return start_row + 1

        next_row = 0
        next_row = add_section("Movies", movies, next_row)
        next_row = add_section("Web Series", series, next_row)

    def populate_grid(self, items, title):
        self.clear_content()
        lbl = ctk.CTkLabel(self.content_frame, text=title, font=("Arial", 26, "bold"), text_color="white")
        lbl.grid(row=0, column=0, sticky="w", pady=(20, 10), padx=10, columnspan=7)

        cols = 7
        row = 1
        col_num = 0

        for col in range(cols):
            self.content_frame.grid_columnconfigure(col, weight=1, uniform="col")

        for item in items:
            card = ctk.CTkFrame(self.content_frame, fg_color="#222222", corner_radius=15)
            card.grid(row=row, column=col_num, padx=8, pady=8, sticky="nsew")

            if os.path.exists(item["poster"]):
                img = Image.open(item["poster"]).resize((160, 250))
                photo = ctk.CTkImage(light_image=img, size=(160, 250))
                self.image_refs.append(photo)
                lbl_img = ctk.CTkLabel(card, image=photo, text="")
                lbl_img.pack(pady=(10, 5))
            else:
                ctk.CTkLabel(card, text="No Image", font=("Arial", 14), text_color="gray").pack(pady=40)

            ctk.CTkLabel(card, text=item["title"], font=("Arial", 14, "bold"), text_color="white",
                         wraplength=160, justify="center").pack(pady=(0, 5))

            info_txt = f"{item['year']} | ⭐ {item['rating']} | {item['language']}"
            ctk.CTkLabel(card, text=info_txt, font=("Arial", 11), text_color="#bbbbbb").pack()

            genres_txt = ", ".join(item["genres"])
            ctk.CTkLabel(card, text=genres_txt, font=("Arial", 10), text_color="#999999",
                         wraplength=160, justify="center").pack(pady=(3, 7))

            desc = item.get("description", "No description available.")
            if len(desc) > 100:
                desc = desc[:97] + "..."
            ctk.CTkLabel(card, text=desc, font=("Arial", 11), text_color="#dddddd",
                         wraplength=160, justify="left").pack(padx=8, pady=(0, 10))

            play_btn = ctk.CTkButton(card, text="▶ Play Now", width=140, height=35, fg_color="#e50914",
                                     hover_color="#b20710", corner_radius=20,
                                     font=("Arial", 13, "bold"),
                                     command=lambda i=item: self.show_trailer_window(i))
            play_btn.pack(pady=(5, 10))

            col_num += 1
            if col_num >= cols:
                col_num = 0
                row += 1

    def show_trailer_window(self, movie):
        try:
            trailer_win = ctk.CTkToplevel(self)
            trailer_win.geometry("900x520")
            trailer_win.title(f"Details - {movie['title']}")
            trailer_win.configure(fg_color="#1c1c1c")
            trailer_win.grab_set()  # Modal window

            # Left frame for poster image
            left_frame = ctk.CTkFrame(trailer_win, width=400, height=500, fg_color="#121212")
            left_frame.pack(side="left", padx=20, pady=20)
            left_frame.pack_propagate(False)

            if os.path.exists(movie.get("poster", "")):
                img = Image.open(movie["poster"]).resize((330, 480))
                photo = ctk.CTkImage(light_image=img, size=(330, 480))
                lbl_img = ctk.CTkLabel(left_frame, image=photo, text="")
                lbl_img.image = photo  # keep reference
                lbl_img.pack(pady=10)
            else:
                ctk.CTkLabel(left_frame, text="No Image Available", font=("Arial", 16), text_color="gray").pack(pady=20)

            # Right frame for details
            right_frame = ctk.CTkFrame(trailer_win, fg_color="#222222", corner_radius=15)
            right_frame.pack(side="left", fill="both", expand=True, pady=20, padx=(0,20))
            right_frame.grid_rowconfigure(2, weight=1)  # Make description expand

            # Title
            ctk.CTkLabel(right_frame, text=movie["title"], font=("Arial", 28, "bold"), text_color="white").grid(row=0, column=0, sticky="w", padx=20, pady=(20,8))

            # Info labels
            info_text = (
                f"Year: {movie['year']}\n"
                f"Rating: ⭐ {movie['rating']}\n"
                f"Language: {movie['language']}\n"
                f"Genres: {', '.join(movie['genres'])}"
            )
            ctk.CTkLabel(right_frame, text=info_text, font=("Arial", 15), text_color="#cccccc", justify="left").grid(row=1, column=0, sticky="w", padx=20, pady=(0,15))

            # Scrollable description box
            desc_frame = ctk.CTkFrame(right_frame, fg_color="#333333", corner_radius=10)
            desc_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

            desc_text = tk.Text(desc_frame, wrap="word", font=("Arial", 14), bg="#333333", fg="white", bd=0, padx=15, pady=15)
            desc_text.insert("1.0", movie.get("description", "No description available."))
            desc_text.configure(state="disabled")
            desc_text.pack(side="left", fill="both", expand=True)

            desc_scroll = tk.Scrollbar(desc_frame, command=desc_text.yview)
            desc_scroll.pack(side="right", fill="y")
            desc_text.configure(yscrollcommand=desc_scroll.set)

            # Buttons frame at bottom right
            btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            btn_frame.grid(row=3, column=0, sticky="e", padx=20, pady=10)

            def open_trailer():
                url = movie.get("trailer_url")
                if url:
                    webbrowser.open(url)
                else:
                    ctk.CTkLabel(right_frame, text="Trailer URL not available.",
                                 font=("Arial", 12), text_color="red").grid(row=4, column=0, sticky="w", padx=20)

            play_btn = ctk.CTkButton(btn_frame, text="▶ Play Now", width=160, height=45,
                                     fg_color="#e50914", hover_color="#b20710",
                                     corner_radius=20, font=("Arial", 16, "bold"),
                                     command=open_trailer)
            play_btn.pack(side="left", padx=(0,15))

            close_btn = ctk.CTkButton(btn_frame, text="GO Back", width=100, height=45,
                                      fg_color="#FF4444", hover_color="#cc0000",
                                      command=trailer_win.destroy)
            close_btn.pack(side="left")

        except Exception as e:
            print("Error opening trailer window:", e)

    def on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfigure(self.content_window, width=self.canvas.winfo_width())

    def on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.content_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    app = MovieApp()
    app.withdraw()  # Hide main window initially

    # Login Window
    login_window = ctk.CTkToplevel()
    login_window.title("LOGIN - MovieMAX")
    login_window.geometry("1000x600")
    login_window.configure(fg_color="black")

    # Background image (optional)
    if os.path.exists("bgimage.jpg"):
        bg_image = Image.open("bgimage.jpg")
        bg = ctk.CTkImage(bg_image, size=(2000, 800))
        bg_label = ctk.CTkLabel(login_window, image=bg, text="")
        bg_label.place(relx=0.5, rely=0.5, anchor="center")

    # Semi-transparent overlay (optional)
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
