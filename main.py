import customtkinter as ctk
from geopy.geocoders import Nominatim
from tkintermapview import TkinterMapView
from backend.booking_system import BookingSystem
from backend.distance import StreetCoordinates
from backend.timesimulation import simulate_time
from backend.vehicle import Motorcycle, Taxi, Car, ElectricCar, Van

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("assets/themes/purple_theme.json")

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
        # Background here
        self.login_frame = ctk.CTkFrame(self, fg_color="#FFFBE4")
        self.login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Dark rounded login panel
        self.bg_panel = ctk.CTkFrame(
            self.login_frame,
            width=600,
            height=1200,
            fg_color="#2b2b2b",
            corner_radius=0
        )
        self.bg_panel.place(x=600, y=0)

        # Now all widgets go INSIDE the dark panel
        ctk.CTkLabel(
            self.bg_panel,
            text="Welcome to Sadride!",
            font=ctk.CTkFont(family="Georgia", size=35)
        ).place(x=94, y=120)

        self.name_entry = ctk.CTkEntry(
            self.bg_panel,
            placeholder_text="Username",
            font=ctk.CTkFont(size=25),
            width=350,
            height=80,
            corner_radius=5
        )
        self.name_entry.place(x=80, y=180)

        ctk.CTkButton(
            self.bg_panel,
            text="Log In",
            font=ctk.CTkFont(size=25),
            width=220,
            height=50,
            corner_radius=5,
            command=self.handle_login
        ).place(x=145, y=280)
        
    def handle_login(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.username = name
        self.main_ui()
        
    def logout(self):
        self.username = ""
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None
        self.start_marker = None
        self.end_marker = None
        self.map_widget = None
        self.vehicle_type = "Car"
        self.login_ui()

    
    def main_ui(self):
        self.clear_widgets()

        # Outer layout container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Tab switcher (top)
        self.tab_control = ctk.CTkSegmentedButton(
            self.main_frame,
            values=["Book Ride", "Manage Bookings"],
            command=self.switch_tab
        )
        self.tab_control.set("Book Ride")
        self.tab_control.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Booking frame
        self.book_frame = ctk.CTkFrame(self.main_frame)
        self.book_frame.grid(row=1, column=0, sticky="nsew")
        
        # Manage bookings frame (hidden initially)
        self.manage_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.manage_frame.grid(row=1, column=0, sticky="nsew")
        self.manage_frame.grid_remove()

        self.setup_booking_ui()

        # --- Bottom-right cancel container ---
        self.cancel_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cancel_container.grid(row=2, column=0, sticky="e", padx=10, pady=5)

        self.cancel_entry = ctk.CTkEntry(self.cancel_container, placeholder_text="Enter Booking ID to cancel", width=200)
        self.cancel_entry.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            self.cancel_container,
            text="Cancel Booking",
            command=self.cancel_booking,
            # fg_color="#6A0DAD",
            # hover_color="#5A0CAD",
            text_color="white",
            corner_radius=8
        )
        cancel_btn.pack(side="left", padx=5)

        self.cancel_result = ctk.CTkLabel(
            self.cancel_container,
            text="",
            text_color="white",
            anchor="w",
            width=300  # Optional: force space for text to align left
        )
        self.cancel_result.pack(side="left", padx=5)

        # Hide initially
        self.cancel_container.grid_remove()

                
    def setup_booking_ui(self):
        # Configure grid layout for responsiveness
        self.book_frame.grid_rowconfigure(1, weight=1)
        self.book_frame.grid_columnconfigure((0, 1), weight=1)

        # Header frame for welcome + logout
        header_frame = ctk.CTkFrame(self.book_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)  # Allow welcome label to expand

        # Welcome label
        welcome_label = ctk.CTkLabel(header_frame, text=f"Welcome, {self.username}", font=ctk.CTkFont(size=20))
        welcome_label.grid(row=0, column=0, sticky="w")

        # Logout button
        logout_btn = ctk.CTkButton(
            header_frame,
            text="Logout",
            width=80,
            height=28,
            command=self.logout,
            fg_color="transparent",
            hover_color="#6A0DAD",
            border_width=1,
            border_color="#6A0DAD",
            text_color="white",
            corner_radius=8
        )
        logout_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Map widget (left side)
        self.map_widget = TkinterMapView(self.book_frame, corner_radius=10)
        self.map_widget.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        self.map_widget.set_position(14.5995, 120.9842)
        self.map_widget.set_zoom(12)
        self.map_widget.add_left_click_map_command(self.handle_map_click)

        # Route data tracking
        self.click_count = 0
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None

        # Right panel (info and controls)
        self.right_panel = ctk.CTkFrame(self.book_frame, corner_radius=10, border_width=1, border_color="#444")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        self.right_panel.grid_rowconfigure(99, weight=1)  # for spacing
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.start_label = ctk.CTkLabel(
            self.right_panel, text="🟢 Start: not set", anchor="w", font=ctk.CTkFont(size=13)
        )
        self.start_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.end_label = ctk.CTkLabel(
            self.right_panel, text="🔴 End: not set", anchor="w", font=ctk.CTkFont(size=13)
        )
        self.end_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        # Vehicle selection buttons
        vehicle_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        vehicle_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        vehicle_frame.grid_columnconfigure((0, 1), weight=1)

        self.vehicle_buttons = {}
        vehicle_types = ["Motorcycle", "Taxi", "Car", "Electric Car", "Van"]

        def set_vehicle_type(vehicle):
            self.vehicle_type = vehicle
            for v_type, btn in self.vehicle_buttons.items():
                btn.configure(
                    fg_color="#b278ff" if v_type == vehicle else "transparent",
                    text_color="white" if v_type == vehicle else "black"
                )
            if self.clicked_start_coord and self.clicked_end_coord:
                self.update_estimates_from_clicks()

        for i, vehicle in enumerate(vehicle_types):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                vehicle_frame, text=vehicle, command=lambda v=vehicle: set_vehicle_type(v),
                fg_color="transparent", text_color="black", border_width=1, border_color="#6A0DAD"
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.vehicle_buttons[vehicle] = btn

        set_vehicle_type("Car")

        # ETA and cost
        self.eta_label = ctk.CTkLabel(self.right_panel, text="🕒 ETA: --")
        self.eta_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))

        self.price_label = ctk.CTkLabel(self.right_panel, text="💰 Total Cost: --")
        self.price_label.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        # Book Ride button
        ctk.CTkButton(self.right_panel, text="Book Ride", command=self.book_ride, corner_radius=20).grid(
            row=6, column=0, padx=10, pady=10, sticky="ew"
        )

    def switch_tab(self, selected):
        if selected == "Book Ride":
            self.manage_frame.grid_remove()
            self.cancel_container.grid_remove()  # ✔ hide cancel section
            self.book_frame.grid()
            self.manage_visible = False
        else:
            self.book_frame.grid_remove()
            self.manage_frame.grid()
            self.cancel_container.grid()         # ✔ show cancel section
            self.manage_visible = True
            self.load_bookings()

            
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

        # Filter bookings for current user only
        df = self.system.view_bookings()
        df = df[df["User"] == self.username]

        if df.empty:
            # Show message if no bookings
            no_booking_label = ctk.CTkLabel(self.manage_frame, text="📭 No bookings yet.", font=ctk.CTkFont(size=14))
            no_booking_label.grid(row=0, column=0, padx=10, pady=20, sticky="w")
            return

        # Header (only shown if there are bookings)
        headers = ["Booking ID", "Status", "User", "Vehicle Type", "From", "To", "Date", "Distance", "Total Cost"]
        header_font = ctk.CTkFont(size=13, weight="bold")
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.manage_frame, text=header, font=header_font, padx=5)
            label.grid(row=0, column=col, sticky="nsew", padx=3, pady=3)

        # Render user bookings
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
                    wraplength=150,
                    font=ctk.CTkFont(size=12)
                )
                label.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                self.manage_frame.grid_columnconfigure(j, weight=1)

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
            if not hasattr(self, "cancel_entry") or not self.cancel_entry:
                return  # Cancel UI not visible or not initialized

            booking_id = int(self.cancel_entry.get())
            df = self.system.view_bookings()

            # Find matching booking
            booking_row = df[df["Booking ID"] == booking_id]

            if booking_row.empty:
                if self.cancel_result:
                    self.cancel_result.configure(text="❌ Booking ID not found.")
                return

            if booking_row.iloc[0]["User"] != self.username:
                if self.cancel_result:
                    self.cancel_result.configure(text="❌ Booking ID not found.")
                return

            # Proceed to cancel
            result = self.system.cancel_booking(booking_id)
            if self.cancel_result:
                self.cancel_result.configure(text=result)
            self.cancel_entry.delete(0, 'end')
            self.load_bookings()
            self.show_toast(result)

        except ValueError:
            if self.cancel_result:
                self.cancel_result.configure(text="❌ Invalid booking ID.")
        except Exception as e:
            if self.cancel_result:
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
