import customtkinter as ctk
from geopy.geocoders import Nominatim
from tkintermapview import TkinterMapView
from backend.booking_system import BookingSystem
from backend.distance import StreetCoordinates
from backend.timesimulation import simulate_time
from backend.vehicle import Motorcycle, Taxi, Car, ElectricCar, Van

ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

class RideApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ride Booking System")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.system = BookingSystem()

        self.username = ""
        self.vehicle_type = "Car"
        self.price_label = None
        self.eta_label = None
        self.map_widget = None
        self.start_marker = None
        self.end_marker = None
        self.manage_visible = False
        self.geolocator = Nominatim(user_agent="ride_booking_app")


        self.login_ui()

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
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=2)

        ctk.CTkLabel(self.main_frame, text=f"Welcome, {self.username}", font=ctk.CTkFont(size=20)).grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

        self.map_widget = TkinterMapView(self.main_frame, corner_radius=10, height=400)
        self.map_widget.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        self.map_widget.set_position(14.5995, 120.9842)
        self.map_widget.set_zoom(12)
        self.map_widget.add_left_click_map_command(self.handle_map_click)
        self.click_count = 0
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None

        self.right_panel = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 10))

        for i in range(10):
            self.right_panel.grid_rowconfigure(i, weight=0)
        self.right_panel.grid_rowconfigure(9, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.start_label = ctk.CTkLabel(
            self.right_panel,
            text="🟢 Start: not set",
            width=250,               # Fixed width
            anchor="w",              # Left align
            wraplength=0,            # Disable wrapping
            font=ctk.CTkFont(size=13)
        )
        self.start_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.end_label = ctk.CTkLabel(
            self.right_panel,
            text="🔴 End: not set",
            width=250,
            anchor="w",
            wraplength=0,
            font=ctk.CTkFont(size=13)
        )
        self.end_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
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
            
            # Immediately update cost and ETA if start and end points are set
            if self.clicked_start_coord and self.clicked_end_coord:
                self.update_estimates_from_clicks()


        for i, vehicle in enumerate(vehicle_types):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(vehicle_frame, text=vehicle, command=lambda v=vehicle: set_vehicle_type(v),
                                fg_color="transparent", text_color="black", border_width=1, border_color="#6A0DAD")
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.vehicle_buttons[vehicle] = btn

        set_vehicle_type("Car")

        self.eta_label = ctk.CTkLabel(self.right_panel, text="🕒 ETA: --")
        self.eta_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))

        self.price_label = ctk.CTkLabel(self.right_panel, text="💰 Total Cost: --")
        self.price_label.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        ctk.CTkButton(self.right_panel, text="Estimate Cost", command=self.update_estimates_from_clicks, corner_radius=20).grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(self.right_panel, text="Book Ride", command=self.book_ride, corner_radius=20).grid(row=5, column=0, padx=10, pady=60, sticky="ew")

        self.manage_toggle_btn = ctk.CTkButton(self.right_panel, text="📋 Manage Bookings", command=self.toggle_manage_bookings, corner_radius=20)
        self.manage_toggle_btn.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.manage_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.manage_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        self.manage_frame.grid_columnconfigure(2, weight=2)
        self.manage_frame.grid_remove()
        
    def get_location_name(self, lat, lon):
        try:
            location = self.geolocator.reverse((lat, lon), exactly_one=True, language='en')
            if location and location.raw and "address" in location.raw:
                address = location.raw["address"]
                # Choose the most general fields you want to include
                city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
                barangay = address.get("neighbourhood") or address.get("suburb")
                province = address.get("state")
                country = address.get("country")
                
                parts = [part for part in [barangay, city, province, country] if part]
                return ", ".join(parts)
            else:
                return f"{lat:.5f}, {lon:.5f}"
        except Exception as e:
            print(f"[Reverse Geocode Error] {e}")
            return f"{lat:.5f}, {lon:.5f}"

    def handle_map_click(self, coords):
        lat, lon = coords

        if self.click_count % 2 == 0:
            # New start point
            self.clicked_start_coord = (lat, lon)
            print(f"[🟢 Start] Lat: {lat}, Lon: {lon}")  # 👈 Print start coordinates

            if self.start_marker:
                self.start_marker.delete()
            self.start_marker = self.map_widget.set_marker(lat, lon, text="Start")
            start_name = self.get_location_name(lat, lon)
            self.start_label.configure(text=f"🟢 Start: {start_name}")


            # Clear old end marker and route
            if self.end_marker:
                self.end_marker.delete()
                self.end_marker = None
            if self.route_path:
                self.route_path.delete()
                self.route_path = None

        else:
            # New end point
            self.clicked_end_coord = (lat, lon)
            print(f"[🔴 End] Lat: {lat}, Lon: {lon}")  # 👈 Print end coordinates

            if self.end_marker:
                self.end_marker.delete()
            self.end_marker = self.map_widget.set_marker(lat, lon, text="End")
            end_name = self.get_location_name(lat, lon)
            self.end_label.configure(text=f"🔴 End: {end_name}")
            
            # Draw route and update estimate
            if self.clicked_start_coord:
                self.route_path = self.map_widget.set_path([self.clicked_start_coord, self.clicked_end_coord])
                self.update_estimates_from_clicks()

        self.click_count += 1


    def update_estimates_from_clicks(self):
        if not (self.clicked_start_coord and self.clicked_end_coord):
            self.price_label.configure(text="❌ Please click both start and end locations on the map.")
            self.eta_label.configure(text="🕒 ETA: --")
            return

        try:
            distance = StreetCoordinates.calculate_distance_from_coords(self.clicked_start_coord, self.clicked_end_coord)
            travel_time = simulate_time(distance, self.vehicle_type)

            vehicle_obj = {
                "Motorcycle": Motorcycle(),
                "Taxi": Taxi(),
                "Car": Car(),
                "Electric Car": ElectricCar(),
                "Van": Van()
            }.get(self.vehicle_type, Car())

            cost = vehicle_obj.calculate_cost(distance, travel_time)

            self.eta_label.configure(text=f"🕒 ETA: {travel_time} minutes")
            self.price_label.configure(text=f"💰 Total Cost: ₱{cost:.2f}")

        except Exception as e:
            self.price_label.configure(text=f"❌ Error calculating estimate: {str(e)}")
            self.eta_label.configure(text="🕒 ETA: --")
    def load_bookings(self):
        # Clear existing rows
        for widget in self.manage_frame.winfo_children():
            widget.destroy()

        # Header
        headers = ["Booking ID", "Status", "User", "Vehicle Type", "From", "To", "Date", "Distance", "Total Cost"]
        header_font = ctk.CTkFont(size=13, weight="bold")
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.manage_frame, text=header, font=header_font, padx=5)
            label.grid(row=0, column=col, sticky="nsew", padx=3, pady=3)

        # Rows
        df = self.system.view_bookings()

        for i, (_, row) in enumerate(df.iterrows(), start=1):
            for j, col in enumerate(headers):
                val = row.get(col, "")
                if col == "Distance":
                    val = f"{float(val):.2f} miles"
                label = ctk.CTkLabel(
                    self.manage_frame,
                    text=str(val),
                    padx=8,
                    anchor="w",
                    wraplength=150,  # Smaller to allow more columns to fit
                    font=ctk.CTkFont(size=12)
                )

                label.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                self.manage_frame.grid_columnconfigure(j, weight=1)

        # Cancel Booking Section
        cancel_frame = ctk.CTkFrame(self.manage_frame, fg_color="transparent")
        cancel_frame.grid(row=1000, column=0, columnspan=len(headers), sticky="w", pady=10)

        self.cancel_entry = ctk.CTkEntry(cancel_frame, placeholder_text="Enter Booking ID to cancel", width=200)
        self.cancel_entry.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(cancel_frame, text="Cancel Booking", command=self.cancel_booking)
        cancel_btn.pack(side="left", padx=5)

        self.cancel_result = ctk.CTkLabel(self.manage_frame, text="")
        self.cancel_result.grid(row=1001, column=0, columnspan=len(headers), sticky="w", padx=5)

    def toggle_manage_bookings(self):
        if self.manage_visible:
            self.manage_frame.grid_remove()
            self.manage_toggle_btn.configure(text="📋 Manage Bookings")
            self.manage_visible = False
        else:
            self.manage_frame.grid()
            self.manage_toggle_btn.configure(text="📋 Hide Bookings")
            self.manage_visible = True
            self.load_bookings()


    def book_ride(self):
        if not self.clicked_start_coord or not self.clicked_end_coord:
            self.price_label.configure(text="❌ Please select both start and end points on the map.")
            return

        try:
            # Get readable locations
            start_loc = self.get_location_name(*self.clicked_start_coord)
            end_loc = self.get_location_name(*self.clicked_end_coord)

            # Compute distance, time, and cost
            distance = StreetCoordinates.calculate_distance_from_coords(
                self.clicked_start_coord, self.clicked_end_coord
            )
            travel_time = simulate_time(distance, self.vehicle_type)

            vehicle_obj = {
                "Motorcycle": Motorcycle(),
                "Taxi": Taxi(),
                "Car": Car(),
                "Electric Car": ElectricCar(),
                "Van": Van()
            }.get(self.vehicle_type, Car())

            cost = vehicle_obj.calculate_cost(distance, travel_time)

            # Save to CSV
            booking_id = self.system.book_ride(
                self.username,
                self.vehicle_type,
                start_loc,
                end_loc,
                distance,
                travel_time
            )

            self.price_label.configure(text=f"✅ Ride booked! Booking ID: {booking_id}")
            if self.manage_visible:
                self.load_bookings()

        except Exception as e:
            self.price_label.configure(text=f"Error: {str(e)}")

                
    def cancel_booking(self):
        try:
            booking_id = int(self.cancel_entry.get())
            result = self.system.cancel_booking(booking_id)
            self.cancel_result.configure(text=result)
            self.cancel_entry.delete(0, 'end')
            self.load_bookings()
            self.show_toast(result)
        except ValueError:
            self.cancel_result.configure(text="❌ Invalid booking ID.")
        except Exception as e:
            self.cancel_result.configure(text=f"❌ Error: {str(e)}")

    def show_toast(self, message, duration=2000):
        toast = ctk.CTkLabel(self, text=message, fg_color="#323232", text_color="white", corner_radius=10, font=ctk.CTkFont(size=14))
        toast.place(relx=0.5, rely=0.05, anchor="n")

        self.after(duration, toast.destroy)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = RideApp()
    app.mainloop()
