import customtkinter as ctk
import csv
from tkintermapview import TkinterMapView
from backend.booking_system import BookingSystem
from backend.distance import StreetCoordinates

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RideApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ride Booking System")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.system = BookingSystem()
        StreetCoordinates()

        self.username = ""
        self.streets = self.load_street_names()
        self.vehicle_type = "Car"
        self.price_label = None
        self.eta_label = None
        self.map_widget = None
        self.start_marker = None
        self.end_marker = None

        self.login_ui()

    def load_street_names(self):
        streets = []
        with open("csv_files/coordinates.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                streets.append(row["Street"].strip())
        return sorted(streets)

    def login_ui(self):
        self.clear_widgets()
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.login_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.login_frame, text="Enter your name to continue", font=ctk.CTkFont(size=18)).grid(row=0, column=0, pady=20)
        self.name_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.name_entry.grid(row=1, column=0, pady=10)
        ctk.CTkButton(self.login_frame, text="Sign In", command=self.handle_login).grid(row=2, column=0, pady=10)

    def handle_login(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.username = name
        self.main_ui()

    def main_ui(self):
        self.clear_widgets()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main_frame, text=f"Welcome, {self.username}", font=ctk.CTkFont(size=18)).grid(row=0, column=0, sticky="w")

        self.tabview = ctk.CTkTabview(self.main_frame, width=850, height=540)
        self.tabview.grid(row=1, column=0, sticky="nsew")

        book_tab = self.tabview.add("Book a Ride")
        manage_tab = self.tabview.add("Manage Bookings")

        book_tab.grid_columnconfigure((0, 1, 2), weight=1)

        self.from_dropdown = ctk.CTkComboBox(book_tab, values=self.streets)
        self.from_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.from_dropdown.set("Select Start Location")

        self.to_dropdown = ctk.CTkComboBox(book_tab, values=self.streets)
        self.to_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.to_dropdown.set("Select End Location")

        self.vehicle_dropdown = ctk.CTkSegmentedButton(book_tab, values=["Motorcycle", "Taxi", "Car", "Electric Car", "Van"])
        self.vehicle_dropdown.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.vehicle_dropdown.set("Car")

        self.map_widget = TkinterMapView(book_tab, corner_radius=10)
        self.map_widget.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.map_widget.set_position(14.5995, 120.9842)
        self.map_widget.set_zoom(6)

        book_tab.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(book_tab, text="Estimate Cost", command=self.show_estimate).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(book_tab, text="Book Ride", command=self.book_ride).grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.eta_label = ctk.CTkLabel(book_tab, text="")
        self.eta_label.grid(row=3, column=0, columnspan=2, sticky="w")

        self.price_label = ctk.CTkLabel(book_tab, text="")
        self.price_label.grid(row=4, column=0, columnspan=2, sticky="w")

        manage_tab.grid_rowconfigure(0, weight=1)
        manage_tab.grid_columnconfigure(0, weight=1)

        self.table_frame = ctk.CTkScrollableFrame(manage_tab)
        self.table_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)

        self.table_headers = ["Booking ID", "Status", "User", "Vehicle Type", "From", "To", "Date", "Distance", "Total Cost"]
        header_font = ctk.CTkFont(size=14, weight="bold")
        for col, header in enumerate(self.table_headers):
            label = ctk.CTkLabel(self.table_frame, text=header, font=header_font, padx=8)
            label.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

        self.booking_rows = []

        ctk.CTkButton(manage_tab, text="Refresh Bookings", command=self.load_bookings).grid(row=1, column=0, pady=5)

        cancel_frame = ctk.CTkFrame(manage_tab)
        cancel_frame.grid(row=2, column=0, pady=10)

        self.cancel_entry = ctk.CTkEntry(cancel_frame, placeholder_text="Enter Booking ID to cancel", width=200)
        self.cancel_entry.pack(side="left", padx=5)

        ctk.CTkButton(cancel_frame, text="Cancel Booking", command=self.cancel_booking).pack(side="left", padx=5)

        self.cancel_result = ctk.CTkLabel(manage_tab, text="")
        self.cancel_result.grid(row=3, column=0)

        self.load_bookings()

    def show_estimate(self):
        start = self.from_dropdown.get().strip()
        end = self.to_dropdown.get().strip()
        vehicle = self.vehicle_dropdown.get()

        if start == end or "Select" in start or "Select" in end:
            self.price_label.configure(text="❌ Please choose two different valid locations.")
            return

        try:
            distance = StreetCoordinates.calculate_distance(start, end)
            from backend.timesimulation import simulate_time
            from backend.vehicle import Motorcycle, Taxi, Car, ElectricCar, Van

            time = simulate_time(distance, vehicle)
            vehicle_obj = {
                "Motorcycle": Motorcycle(),
                "Taxi": Taxi(),
                "Car": Car(),
                "Electric Car": ElectricCar(),
                "Van": Van()
            }.get(vehicle, Car())

            cost = vehicle_obj.calculate_cost(distance, time)

            self.eta_label.configure(text=f"🕒 Estimated Time: {time} minutes")
            self.price_label.configure(text=f"💰 Total Cost: ₱{cost:.2f}")

            self.draw_route_on_map(start, end)

        except Exception as e:
            self.price_label.configure(text=f"Error: {str(e)}")

    def draw_route_on_map(self, start, end):
        coords = StreetCoordinates.street_coords
        start_coord = coords[start]
        end_coord = coords[end]

        if self.start_marker:
            self.start_marker.delete()
        if self.end_marker:
            self.end_marker.delete()

        self.start_marker = self.map_widget.set_marker(start_coord[0], start_coord[1], text="Start")
        self.end_marker = self.map_widget.set_marker(end_coord[0], end_coord[1], text="End")
        self.map_widget.set_path([start_coord, end_coord])
        self.map_widget.set_position(start_coord[0], start_coord[1])

    def book_ride(self):
        start = self.from_dropdown.get().strip()
        end = self.to_dropdown.get().strip()
        vehicle = self.vehicle_dropdown.get()

        try:
            booking_id = self.system.book_ride(self.username, vehicle, start, end)
            self.price_label.configure(text=f"✅ Ride booked! Booking ID: {booking_id}")
        except Exception as e:
            self.price_label.configure(text=f"Error: {str(e)}")

    def load_bookings(self):
        for row in self.booking_rows:
            for widget in row:
                widget.destroy()
        self.booking_rows.clear()

        df = self.system.view_bookings()
        if df.empty:
            label = ctk.CTkLabel(self.table_frame, text="No bookings found.")
            label.grid(row=1, column=0, columnspan=len(self.table_headers), pady=10)
            self.booking_rows.append([label])
        else:
            for i, (_, row) in enumerate(df.iterrows(), start=1):
                row_widgets = []
                for j, col in enumerate(self.table_headers):
                    if col == "Distance":
                        text = f"{float(row[col]):.2f} miles"
                    else:
                        text = str(row[col]) if col in row else ""
                    label = ctk.CTkLabel(self.table_frame, text=text, padx=8, anchor="w", wraplength=140)
                    label.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                    row_widgets.append(label)
                self.booking_rows.append(row_widgets)

    def cancel_booking(self):
        try:
            booking_id = int(self.cancel_entry.get())
            result = self.system.cancel_booking(booking_id)
            self.cancel_result.configure(text=result)
            self.load_bookings()
        except ValueError:
            self.cancel_result.configure(text="Invalid booking ID.")
   
    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = RideApp()
    app.mainloop()
