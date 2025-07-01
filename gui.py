import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ResizableBackgroundApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Car Ride UI")

        self.original_image = Image.open(image_path)

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.background_image = None

        self.root.bind("<Configure>", self.on_resize)
        self.root.after_idle(self.show_main_view)

    def clear_widgets(self):
        self.canvas.delete("all")

    def show_main_view(self):
        self.clear_widgets()

        # Frame to contain the buttons for size alignment
        self.button_frame = tk.Frame(self.canvas, bg="", highlightthickness=0)

        # Common style
        button_style = {
            "font": ("Segoe UI", 16),
            "width": 16,     # in characters
            "height": 2,
            "padx": 10,
            "pady": 5
        }

        # History Button
        self.history_button = tk.Button(
            self.button_frame,
            text="View all Bookings",
            command=self.show_history_view,
            **button_style
        )

        # Book Button
        self.booking_button = tk.Button(
            self.button_frame,
            text="Book a Ride",
            command=self.book_ride,
            **button_style
        )

        # Pack buttons vertically inside the frame
        self.history_button.pack(pady=(0, 10))
        self.booking_button.pack()

        # Add the frame to the canvas
        self.button_frame_window = self.canvas.create_window(
            0, 0, window=self.button_frame, anchor="center"
        )

        self.update_layout()

    def show_history_view(self):
        self.clear_widgets()

        bookings = [
            ("R001", "Sedan", "Robert", "Quezon City", "Pasig", "₱180"),
            ("R002", "SUV", "Robert", "Pasig", "Taguig", "₱220"),
            ("R003", "Van", "Robert", "Taguig", "Binangonan", "₱300"),
            ("R001", "Sedan", "Robert", "Quezon City", "Pasig", "₱180"),
            ("R002", "SUV", "Robert", "Pasig", "Taguig", "₱220"),
            ("R003", "Van", "Robert", "Taguig", "Binangonan", "₱300"),
            ("R001", "Sedan", "Robert", "Quezon City", "Pasig", "₱180"),
            ("R002", "SUV", "Robert", "Pasig", "Taguig", "₱220"),
            ("R003", "Van", "Robert", "Taguig", "Binangonan", "₱300"),
            ("R001", "Sedan", "Robert", "Quezon City", "Pasig", "₱180"),
        ]

        columns = ("ID", "Vehicle Type", "User", "Pickoff", "Dropoff", "Fare")
        self.tree = ttk.Treeview(self.canvas, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        for row in bookings:
            self.tree.insert("", "end", values=row)

        self.table_window = self.canvas.create_window(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            window=self.tree, anchor="center"
        )

        self.back_button = tk.Button(
            self.canvas, text="Back", command=self.show_main_view,
            font=("Segoe UI", 12), bg="#FFFFFF"
        )

        self.back_button_window = self.canvas.create_window(
            self.canvas.winfo_width() - 10,
            10,
            window=self.back_button,
            anchor="ne"
        )

        self.update_layout()

    def book_ride(self):
        print("🚗 Booking a ride!")

    def on_resize(self, event):
        self.root.after(10, self.update_layout)

    def update_layout(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 1 or height < 1:
            return

        # Update background image
        resized = self.original_image.resize((width, height), Image.LANCZOS)
        self.background_image = ImageTk.PhotoImage(resized)
        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw", tags="bg")

        # Reposition elements if they exist
        if hasattr(self, 'button_frame_window'):
            self.canvas.coords(self.button_frame_window, width // 2, height // 2)
        if hasattr(self, 'table_window'):
            self.canvas.coords(self.table_window, width // 2, height // 2)
        if hasattr(self, 'back_button_window'):
            self.canvas.coords(self.back_button_window, width - 10, 10)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = ResizableBackgroundApp(root, "background.jpg")  # Replace with your image
    root.mainloop()
