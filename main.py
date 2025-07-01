import customtkinter as ctk
import csv
from tkintermapview import TkinterMapView
from backend.booking_system import BookingSystem
from backend.distance import StreetCoordinates

ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

class RideApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ride Booking System")
        self.geometry("1000x700")
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
        self.manage_visible = False

        self.login_ui()

    def load_street_names(self):
        streets = []
        try:
            with open("csv_files/coordinates.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    streets.append(row["Street"].strip())
        except FileNotFoundError:
            # Fallback streets if CSV file is not found
            streets = ["Quezon Avenue", "EDSA", "Commonwealth Avenue", "Katipunan Avenue", "C.P. Garcia Avenue"]
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
        self.main_frame.grid_columnconfigure(0, weight=3)  # map column
        self.main_frame.grid_columnconfigure(1, weight=2)  # right panel column
        self.main_frame.grid_rowconfigure(0, weight=0)    # welcome row
        self.main_frame.grid_rowconfigure(1, weight=1)    # main content row
        self.main_frame.grid_rowconfigure(2, weight=2)  # manage frame row


        # Welcome message above the map
        ctk.CTkLabel(self.main_frame, text=f"Welcome, {self.username}", font=ctk.CTkFont(size=20)).grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

        # Map on the left
        self.map_widget = TkinterMapView(self.main_frame, corner_radius=10, height=400)
        self.map_widget.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        self.map_widget.set_position(14.5995, 120.9842)
        self.map_widget.set_zoom(12)
        self.map_widget.add_left_click_map_command(self.handle_map_click)
        self.click_count = 0
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None  # This will store the current drawn path


        # Right Panel: Booking + Manage Section
        self.right_panel = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 10))

        # Define grid rows clearly
        for i in range(10):
            self.right_panel.grid_rowconfigure(i, weight=0)
        self.right_panel.grid_rowconfigure(9, weight=1)  # For manage_frame

        self.right_panel.grid_columnconfigure(0, weight=1)

        # Start/End Location Dropdowns
        self.from_dropdown = ctk.CTkComboBox(self.right_panel, values=self.streets)
        self.from_dropdown.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.from_dropdown.set("Select Start Location")

        self.to_dropdown = ctk.CTkComboBox(self.right_panel, values=self.streets)
        self.to_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.to_dropdown.set("Select End Location")

        # Vehicle Type Buttons
        vehicle_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        vehicle_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        vehicle_frame.grid_columnconfigure((0, 1), weight=1)

        self.vehicle_buttons = {}
        vehicle_types = ["Motorcycle", "Taxi", "Car", "Electric Car", "Van"]

        def set_vehicle_type(vehicle):
            self.vehicle_type = vehicle
            for v_type, btn in self.vehicle_buttons.items():
                btn.configure(
                fg_color="#6A0DAD" if v_type == vehicle else "transparent",
                text_color="white" if v_type == vehicle else "black"
            )

        for i, vehicle in enumerate(vehicle_types):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(vehicle_frame, text=vehicle, command=lambda v=vehicle: set_vehicle_type(v),
                    fg_color="transparent", text_color="black", border_width=1, border_color="#6A0DAD")
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.vehicle_buttons[vehicle] = btn

        set_vehicle_type("Car")

        # Set default vehicle
        set_vehicle_type("Car")

        self.eta_label = ctk.CTkLabel(self.right_panel, text="🕒 ETA: --")
        self.eta_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))

        self.price_label = ctk.CTkLabel(self.right_panel, text="💰 Total Cost: --")
        self.price_label.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        # Separated rounded buttons
        ctk.CTkButton(self.right_panel, text="Estimate Cost", command=self.show_estimate, corner_radius=20).grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(self.right_panel, text="Book Ride", command=self.book_ride, corner_radius=20).grid(row=5, column=0, padx=10, pady=60, sticky="ew")

        # Manage Bookings Button
        self.manage_toggle_btn = ctk.CTkButton(self.right_panel, text="📋 Manage Bookings", command=self.toggle_manage_bookings, corner_radius=20)
        self.manage_toggle_btn.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="ew")

       # Manage Bookings Section under the map
        self.manage_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.manage_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0,10))
        self.manage_frame.grid_columnconfigure(2, weight=2)
        self.manage_frame.grid_remove()  # initially hidden

        # Add table headers
        self.table_headers = ["Booking ID", "Status", "User", "Vehicle Type", "From", "To", "Date", "Distance", "Total Cost"]
        header_font = ctk.CTkFont(size=13, weight="bold")
        for col, header in enumerate(self.table_headers):
            label = ctk.CTkLabel(self.manage_frame, text=header, font=header_font, padx=5)
            label.grid(row=0, column=col, sticky="w", padx=3, pady=3)

        self.booking_rows = []

        # Cancel section
        cancel_frame = ctk.CTkFrame(self.manage_frame, fg_color="transparent")
        cancel_frame.grid(row=1000, column=0, columnspan=10, sticky="w", pady=10)

        self.cancel_entry = ctk.CTkEntry(cancel_frame, placeholder_text="Enter Booking ID to cancel", width=200)
        self.cancel_entry.pack(side="left", padx=5)

        ctk.CTkButton(cancel_frame, text="Cancel Booking", command=self.cancel_booking).pack(side="left", padx=5)

        self.cancel_result = ctk.CTkLabel(self.manage_frame, text="")
        self.cancel_result.grid(row=1001, column=0, columnspan=10, sticky="w", padx=5)
    def handle_map_click(self, coords):
        lat, lon = coords

        if self.click_count % 2 == 0:
            # New START location → reset everything
            self.clicked_start_coord = (lat, lon)

            # ✅ Clear existing markers
            if self.start_marker:
                self.start_marker.delete()
                self.start_marker = None
            if self.end_marker:
                self.end_marker.delete()
                self.end_marker = None

            # ✅ Clear the existing route path
            if self.route_path:
                self.route_path.delete()
                self.route_path = None

            # ✅ Set new start marker
            self.start_marker = self.map_widget.set_marker(lat, lon, text="Start")
            print(f"🟢 Start set to: {lat}, {lon}")

        else:
            # New END location → just update end marker and draw route
            self.clicked_end_coord = (lat, lon)

            if self.end_marker:
                self.end_marker.set_position(lat, lon)
            else:
                self.end_marker = self.map_widget.set_marker(lat, lon, text="End")
            print(f"🔴 End set to: {lat}, {lon}")

            # ✅ Draw new path
            self.route_path = self.map_widget.set_path([
                self.clicked_start_coord,
                self.clicked_end_coord
            ])
            # ✅ Now compute and show distance
            if self.clicked_start_coord and self.clicked_end_coord:
                try:
                    distance = StreetCoordinates.calculate_distance_from_coords(
                        self.clicked_start_coord, self.clicked_end_coord
                    )
                    print(f"📏 Distance: {distance:.2f} miles")
                    self.price_label.configure(text=f"💰 Distance: {distance:.2f} miles")
                except Exception as e:
                    print(f"[Distance Error] {e}")

        self.click_count += 1

    def toggle_manage_bookings(self):
        """Toggle the visibility of the manage bookings section"""
        if self.manage_visible:
            self.manage_frame.grid_remove()
            self.manage_toggle_btn.configure(text="📋 Show Manage Bookings")
            self.manage_visible = False
        else:
            self.manage_frame.grid()
            self.manage_toggle_btn.configure(text="📋 Hide Manage Bookings")
            self.manage_visible = True
            self.load_bookings()

    def show_estimate(self):
        start = self.from_dropdown.get().strip()
        end = self.to_dropdown.get().strip()
        vehicle = self.vehicle_type  # FIXED

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
        try:
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
        except Exception as e:
            print(f"Error drawing route on map: {e}")

    def book_ride(self):
        start = self.from_dropdown.get().strip()
        end = self.to_dropdown.get().strip()
        vehicle = self.vehicle_type  # FIXED

        if start == end or "Select" in start or "Select" in end:
            self.price_label.configure(text="❌ Please choose two different valid locations.")
            return

        try:
            booking_id = self.system.book_ride(self.username, vehicle, start, end)
            self.price_label.configure(text=f"✅ Ride booked! Booking ID: {booking_id}")
            if self.manage_visible:
                self.load_bookings()
        except Exception as e:
            self.price_label.configure(text=f"Error: {str(e)}")


    def load_bookings(self):
        # Clear existing booking rows
        for row in self.booking_rows:
            for widget in row:
                widget.destroy()
        self.booking_rows.clear()

        try:
            df = self.system.view_bookings()
            if df.empty:
                label = ctk.CTkLabel(self.manage_frame, text="No bookings found.")
                label.grid(row=1, column=0, columnspan=len(self.table_headers), pady=10)
                self.booking_rows.append([label])
            else:
                for i, (_, row) in enumerate(df.iterrows(), start=1):
                    row_widgets = []
                    for j, col in enumerate(self.table_headers):
                        if col == "Distance":
                            text = f"{float(row[col]):.2f} miles" if col in row else ""
                        else:
                            text = str(row[col]) if col in row else ""
                        label = ctk.CTkLabel(self.manage_frame, text=text, padx=8, anchor="w", wraplength=140)
                        label.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                        row_widgets.append(label)
                    self.booking_rows.append(row_widgets)
        except Exception as e:
            error_label = ctk.CTkLabel(self.manage_frame, text=f"Error loading bookings: {str(e)}")
            error_label.grid(row=1, column=0, columnspan=len(self.table_headers), pady=10)
            self.booking_rows.append([error_label])

    def cancel_booking(self):
        try:
            booking_id = int(self.cancel_entry.get())
            result = self.system.cancel_booking(booking_id)
            self.cancel_result.configure(text=result)
            self.cancel_entry.delete(0, 'end')  # Clear the entry field
            self.load_bookings()  # Refresh the bookings display
        except ValueError:
            self.cancel_result.configure(text="Invalid booking ID. Please enter a number.")
        except Exception as e:
            self.cancel_result.configure(text=f"Error: {str(e)}")
   
    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = RideApp()
    app.mainloop()