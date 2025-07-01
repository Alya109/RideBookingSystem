import customtkinter as ctk
from backend.booking_system import BookingSystem

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RideBookingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.system = BookingSystem()
        self.title("SadRide - Booking System")
        self.geometry("600x500")

        self.username = None
        self.init_login_ui()

    def init_login_ui(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(expand=True)

        ctk.CTkLabel(self.login_frame, text="Enter your name:").pack(pady=10)
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_entry.pack(pady=10)

        ctk.CTkButton(self.login_frame, text="Continue", command=self.start_main_ui).pack(pady=10)

    def start_main_ui(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            return

        self.login_frame.destroy()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        self.book_tab = self.tabview.add("Book Ride")
        self.view_tab = self.tabview.add("View Bookings")
        self.cancel_tab = self.tabview.add("Cancel Booking")

        self.build_book_tab()
        self.build_view_tab()
        self.build_cancel_tab()

    def build_book_tab(self):
        ctk.CTkLabel(self.book_tab, text="Select vehicle:").pack(pady=5)
        self.vehicle_option = ctk.CTkOptionMenu(self.book_tab, values=self.system.get_vehicle_names())
        self.vehicle_option.pack()

        ctk.CTkLabel(self.book_tab, text="From:").pack()
        self.start_entry = ctk.CTkEntry(self.book_tab)
        self.start_entry.pack()

        ctk.CTkLabel(self.book_tab, text="To:").pack()
        self.end_entry = ctk.CTkEntry(self.book_tab)
        self.end_entry.pack()

        ctk.CTkLabel(self.book_tab, text="Group size (for vans):").pack()
        self.group_entry = ctk.CTkEntry(self.book_tab)
        self.group_entry.pack()

        ctk.CTkButton(self.book_tab, text="Book", command=self.book_ride).pack(pady=10)
        self.book_result = ctk.CTkLabel(self.book_tab, text="")
        self.book_result.pack()

    def book_ride(self):
        vehicle = self.vehicle_option.get()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        group_size = int(self.group_entry.get() or 1)

        try:
            booking_id = self.system.book_ride(self.username, vehicle, start, end, group_size)
            self.book_result.configure(text=f"Success! Booking ID: {booking_id}")
            self.build_view_tab(refresh=True)
        except Exception as e:
            self.book_result.configure(text=f"Error: {e}")

    def build_view_tab(self, refresh=False):
        for widget in self.view_tab.winfo_children():
            widget.destroy()

        import pandas as pd
        try:
            df = pd.read_csv("csv_files/bookings.csv")
            if df.empty:
                ctk.CTkLabel(self.view_tab, text="No bookings.").pack()
            else:
                for _, row in df.iterrows():
                    label = ctk.CTkLabel(self.view_tab, text=f"{row['Booking ID']} | {row['User']} | {row['Vehicle Type']} | {row['From']} to {row['To']} | {row['Status']} | {row['Total Cost']}")
                    label.pack(anchor="w")
        except FileNotFoundError:
            ctk.CTkLabel(self.view_tab, text="bookings.csv not found").pack()

    def build_cancel_tab(self):
        ctk.CTkLabel(self.cancel_tab, text="Enter Booking ID to cancel:").pack(pady=5)
        self.cancel_entry = ctk.CTkEntry(self.cancel_tab)
        self.cancel_entry.pack()
        ctk.CTkButton(self.cancel_tab, text="Cancel Booking", command=self.cancel_booking).pack(pady=5)
        self.cancel_result = ctk.CTkLabel(self.cancel_tab, text="")
        self.cancel_result.pack()

    def cancel_booking(self):
        bid = self.cancel_entry.get().strip()
        if bid.isdigit():
            result = self.system.cancel_booking(int(bid))
            self.cancel_result.configure(text=result)
            self.build_view_tab(refresh=True)
        else:
            self.cancel_result.configure(text="Invalid ID")

if __name__ == "__main__":
    app = RideBookingApp()
    app.mainloop()
