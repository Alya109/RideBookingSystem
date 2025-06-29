from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os


# Base window setup
window = Tk()
window.title("Ride Booking System")
window.geometry("420x700")
window.configure(bg="#eaf6fb")  # Softer background

# Top frame for logo and title
top_frame = Frame(
    window,
    bg="#035891",
    height=90
)
top_frame.pack(fill="x", side="top")

# Logo
logo_img = Image.open("assets/logo/app_logo.png")
logo_img = logo_img.resize((60, 60))
logo_photo = ImageTk.PhotoImage(logo_img)
logo_label = Label(top_frame, image=logo_photo, bg="#035891")
logo_label.pack(side="left", padx=18, pady=15)

text_label = Label(
    top_frame,
    text="Sadride",
    font=("Segoe UI", 22, "bold"),
    fg="#fff",
    bg="#035891"
)
text_label.pack(side="left", padx=10)

# Decorative separator
separator = Frame(
    window,
    bg="#3498db",
    height=3
)
separator.pack(fill="x", pady=(0, 18))

# Main content frame
main_frame = Frame(window, bg="#eaf6fb")
main_frame.pack(fill="both", expand=True, padx=24, pady=10)

# Welcome message
welcome_label = Label(
    main_frame,
    text="Welcome to Sadride!",
    font=("Segoe UI", 16, "bold"),
    fg="#035891",
    bg="#eaf6fb"
)
welcome_label.pack(pady=(10, 6))

desc_label = Label(
    main_frame,
    text="Book your ride quickly and safely.",
    font=("Segoe UI", 12),
    fg="#555",
    bg="#eaf6fb"
)
desc_label.pack(pady=(0, 20))

# Entry fields replaced with Combobox
pickup_label = Label(main_frame, text="Pickup Location", font=("Segoe UI", 11), bg="#eaf6fb")
pickup_label.pack(anchor="w", pady=(0, 2))
pickup_options = ["Downtown", "Airport", "Mall", "University", "Train Station"]
pickup_combobox = ttk.Combobox(main_frame, values=pickup_options, font=("Segoe UI", 11), state="readonly")
pickup_combobox.pack(fill="x", pady=(0, 10))
pickup_combobox.current(0)

drop_label = Label(main_frame, text="Drop-off Location", font=("Segoe UI", 11), bg="#eaf6fb")
drop_label.pack(anchor="w", pady=(0, 2))
drop_options = ["Downtown", "Airport", "Mall", "University", "Train Station"]
drop_combobox = ttk.Combobox(main_frame, values=drop_options, font=("Segoe UI", 11), state="readonly")
drop_combobox.pack(fill="x", pady=(0, 20))
drop_combobox.current(1)

# Book button
book_btn = Button(
    main_frame,
    text="Book Ride",
    font=("Segoe UI", 13, "bold"),
    bg="#035891",
    fg="#fff",
    activebackground="#3498db",
    activeforeground="#fff",
    bd=0,
    relief="flat",
    height=2,
    cursor="hand2"
)
book_btn.pack(fill="x", pady=(10, 20))

# Add a subtle footer
footer = Label(
    window,
    text="© 2024 Sadride. All rights reserved.",
    font=("Segoe UI", 9),
    fg="#888",
    bg="#eaf6fb"
)
footer.pack(side="bottom", pady=8)

window.mainloop()