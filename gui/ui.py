import customtkinter as ctk
from threading import Thread
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
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
        
        self.theme_mode = "light"       
        self.active_tab = "Book Ride"   
        
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
        self.geolocator = Nominatim(
            user_agent="ride_booking_app",
            timeout=5,
        )
        self.login_ui()
        
    # For threading support
    def threaded(fn):
        def wrapper(*args, **kwargs):
            Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
        return wrapper

    def login_ui(self):
        self.clear_widgets()

        # Light purple background
        self.login_frame = ctk.CTkFrame(self, fg_color="#dcc7e3")
        self.login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Rounded dark card in center
        self.bg_panel = ctk.CTkFrame(
            self.login_frame,
            width=460,
            height=420,
            fg_color="#2d2d2d",
            corner_radius=20
        )
        self.bg_panel.place(relx=0.5, rely=0.5, anchor="center")
        self.bg_panel.grid_columnconfigure(0, weight=1)

        # Title Label
        ctk.CTkLabel(
            self.bg_panel,
            text="Sadride",
            font=ctk.CTkFont(family="Georgia", size=38, weight="bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, pady=(40, 10), padx=20)

        # Subtitle
        ctk.CTkLabel(
            self.bg_panel,
            text="Safe and Dry Ride.\nBook your ride now!",
            font=ctk.CTkFont(size=16),
            text_color="#cccccc"
        ).grid(row=1, column=0, pady=(0, 30), padx=20)

        # Username Entry
        self.name_entry = ctk.CTkEntry(
            self.bg_panel,
            placeholder_text="Enter username",
            font=ctk.CTkFont(size=18),
            width=260,
            height=50,
            corner_radius=8
        )
        self.name_entry.grid(row=2, column=0, pady=(0, 10), padx=40)

        # Warning Label (initially empty)
        self.warning_label = ctk.CTkLabel(
            self.bg_panel,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="red"
        )
        self.warning_label.grid(row=3, column=0, pady=(0, 10))

        # Login Button
        ctk.CTkButton(
            self.bg_panel,
            text="Log In",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=220,
            height=45,
            corner_radius=8,
            fg_color="#b278ff",
            hover_color="#a162e6",
            text_color="white",
            command=self.handle_login
        ).grid(row=4, column=0, pady=(0, 30))
        
        # Enter key to login in login screen
        self.bind("<Return>", lambda event: self.handle_login())
        
    def handle_login(self):
        username = self.name_entry.get().strip()
        if not username:
            self.warning_label.configure(text="Please enter a username.")
            return

        self.warning_label.configure(text="")
        self.username = username

        self.main_ui()  # Create widgets first

        # THEN apply theme and sync toggle
        ctk.set_appearance_mode(self.theme_mode)
        self.apply_theme()  # Optional: to reskin if switching between logins

        if self.theme_mode == "dark":
            self.theme_toggle.select()
        else:
            self.theme_toggle.deselect()

    def logout(self):
        self.username = ""
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None
        self.start_marker = None
        self.end_marker = None
        self.map_widget = None
        self.vehicle_type = "Car"
        self.unbind("<Return>")

        self.login_ui()

    
    def main_ui(self):
        self.clear_widgets()

        # Outer layout container
        self.main_frame = ctk.CTkFrame(self, fg_color="#f7f1ff")
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
        self.book_frame = ctk.CTkFrame(self.main_frame, fg_color="#f5e9ff")
        self.book_frame.grid(row=1, column=0, sticky="nsew")
        
        # Manage bookings frame (hidden initially)
        self.manage_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#2a2a2a" if self.theme_mode == "dark" else "#f3dbfb"
        )
        self.manage_frame.grid(row=1, column=0, sticky="nsew")
        self.manage_frame.grid_remove()

        self.setup_booking_ui()

        # --- Bottom‑right manage‑toolbar (Cancel / Finish) ---
        self.cancel_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cancel_container.grid(row=2, column=0, sticky="e", padx=10, pady=5)

        # Booking ID entry
        vcmd = self.register(lambda P: P.isdigit() or P == "")
        self.booking_id_entry = ctk.CTkEntry(
            self.cancel_container,
            placeholder_text="Booking ID",
            width=160,
            validate="key",
            validatecommand=(vcmd, "%P")
)
        self.booking_id_entry.pack(side="left", padx=5)

        # Cancel button
        ctk.CTkButton(
            self.cancel_container,
            text="Cancel",
            command=self.cancel_booking,
            fg_color="#d9534f",
            hover_color="#c7423e",
            width=90,
            corner_radius=6,
        ).pack(side="left", padx=(0, 5))

        # Finish button
        ctk.CTkButton(
            self.cancel_container,
            text="Finish",
            command=self.finish_booking,
            fg_color="#5cb85c",
            hover_color="#4ba34b",
            width=90,
            corner_radius=6,
        ).pack(side="left")

        # Status / result label
        self.manage_result = ctk.CTkLabel(
            self.cancel_container,
            text="",
            text_color="white",
            anchor="w",
            width=260
        )
        self.manage_result.pack(side="left", padx=8)
        self.cancel_container.grid_remove()
        
        self.unbind("<Return>")  # Prevent Enter from doing anything here


    def apply_theme(self):
        """Re‑skin existing widgets after self.theme_mode changes."""
        # background colors
        main_bg  = "#f7f1ff" if self.theme_mode == "light" else "#1e1e1e"
        book_bg  = "#f5e9ff" if self.theme_mode == "light" else "#2a2a2a"
        right_bg = "#ffffff" if self.theme_mode == "light" else "#2b2b2b"
        manage_bg= "#f3dbfb" if self.theme_mode == "light" else "#2a2a2a"

        # major frames (check they exist first)
        if hasattr(self, "main_frame"):
            self.main_frame.configure(fg_color=main_bg)
        if hasattr(self, "book_frame"):
            self.book_frame.configure(fg_color=book_bg)
        if hasattr(self, "right_panel"):
            self.right_panel.configure(fg_color=right_bg)
        if hasattr(self, "manage_frame"):
            self.manage_frame.configure(fg_color=manage_bg)

        # text colour in manage‑bookings list
        if hasattr(self, "manage_frame") and self.active_tab == "Manage Bookings":
            fg = "#ffffff" if self.theme_mode == "dark" else "#000000"
            for child in self.manage_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=fg)

    def toggle_theme(self):
        # Now we’re checking a boolean
        self.theme_mode = "dark" if self.theme_toggle.get() else "light"
        ctk.set_appearance_mode(self.theme_mode)

        # Update toggle visuals
        self.theme_toggle.configure(
            text="🌙" if self.theme_mode == "light" else "☀️",
            fg_color="#cccccc" if self.theme_mode == "light" else "#2b2b2b",
            progress_color="#6C0DAF" if self.theme_mode == "light" else "#b278ff"
        )

        self.apply_theme()

        if getattr(self, "manage_visible", False):
            self.load_bookings()

    def setup_booking_ui(self):
        # Configure grid layout for responsiveness
        self.book_frame.grid_rowconfigure(1, weight=1)
        self.book_frame.grid_columnconfigure((0, 1), weight=1)

        # Header frame for welcome + logout
        header_frame = ctk.CTkFrame(self.book_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # Welcome label
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome, {self.username}",
            font=ctk.CTkFont(size=20)
        )
        welcome_label.pack(side="left", anchor="w")

        # Right: container for logout and toggle
        right_controls = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_controls.pack(side="right", anchor="e", padx=(10, 0))

        # Logout button
        logout_btn = ctk.CTkButton(
            right_controls,
            text="Logout",
            width=70,
            command=self.logout,
            fg_color="transparent",
            hover_color="#b278ff",
            border_width=1,
            border_color="#6C0DAF",
            text_color="black",
            corner_radius=8
        )
        logout_btn.grid(row=0, column=0, padx=(0, 5))

        # Theme switch
        self.theme_toggle = ctk.CTkSwitch(
            right_controls,
            text="🌙",
            command=self.toggle_theme,
            onvalue=True,
            offvalue=False
        )
        self.theme_toggle.grid(row=0, column=1)
        
        # Map widget (left side)
        self.map_widget = TkinterMapView(self.book_frame, corner_radius=10)
        # Change tile color depending on theme
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png")
        self.map_widget.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        self.map_widget.set_position(14.5995, 120.9842)
        self.map_widget.set_zoom(12)
        self.map_widget.canvas_tile_fade = False
        self.map_widget.add_left_click_map_command(self.handle_map_click)

        # Route data tracking
        self.click_count = 0
        self.clicked_start_coord = None
        self.clicked_end_coord = None
        self.route_path = None

        # Right panel (info and controls)
        self.right_panel = ctk.CTkFrame(
            self.book_frame,
            corner_radius=10,
            border_width=1,
            border_color="#444",
            fg_color="#2b2b2b" if self.theme_mode == "dark" else "#f5e9ff"
        )
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        self.right_panel.grid_rowconfigure(99, weight=1)
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
        vehicle_types = {
            "🛵 Motorcycle": "Motorcycle",
            "🚕 Taxi": "Taxi",
            "🚗 Car": "Car",
            "⚡ Electric Car": "Electric Car",
            "🚐 Van": "Van"
        }
        
        def set_vehicle_type(vehicle):
            self.vehicle_type = vehicle
            for v_type, btn in self.vehicle_buttons.items():
                if v_type == vehicle:
                    btn.configure(
                        fg_color="#b278ff",
                        text_color="white",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        border_width=2,
                        border_color="#6A0DAD"
                    )
                else:
                    btn.configure(
                        fg_color="transparent",
                        text_color="black",
                        font=ctk.CTkFont(size=13),
                        border_width=1,
                        border_color="#6A0DAD"
                    )
            if self.clicked_start_coord and self.clicked_end_coord:
                self.update_estimates_from_clicks()


        for i, (label, vehicle_name) in enumerate(vehicle_types.items()):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                vehicle_frame,
                text=label,
                command=lambda v=vehicle_name: set_vehicle_type(v),
                fg_color="transparent",
                text_color="black",
                border_width=1,
                border_color="#6A0DAD"
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.vehicle_buttons[vehicle_name] = btn



        set_vehicle_type("Car")

        # ETA and cost
        self.eta_label = ctk.CTkLabel(self.right_panel, text="🕒 ETA: --", font=ctk.CTkFont(size=20, weight="bold"))
        self.eta_label.grid(row=3, column=0, sticky="w", padx=10, pady=(10, 2))

        self.price_label = ctk.CTkLabel(self.right_panel, text="💰 Total Cost: --", font=ctk.CTkFont(size=20, weight="bold"))
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
        self.active_tab = selected

            
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

    @threaded
    def reverse_geocode_start(self, lat, lon):
        name = self.get_location_name(lat, lon)
        self.after(0, lambda: self.start_label.configure(text=f"🟢 Start: {name}"))

    @threaded
    def reverse_geocode_end(self, lat, lon):
        name = self.get_location_name(lat, lon)
        self.after(0, lambda: self.end_label.configure(text=f"🔴 End: {name}"))

    def handle_map_click(self, coords):
        lat, lon = coords

        if self.click_count % 2 == 0:
            # New start point
            self.clicked_start_coord = (lat, lon)
            print(f"[🟢 Start] Lat: {lat}, Lon: {lon}")
            self.show_toast("Start location set.")

            if self.start_marker:
                self.start_marker.delete()
            self.start_marker = self.map_widget.set_marker(lat, lon, text="Start")
            self.reverse_geocode_start(lat, lon)

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
            print(f"[🔴 End] Lat: {lat}, Lon: {lon}")

            if self.end_marker:
                self.end_marker.delete()
            self.end_marker = self.map_widget.set_marker(lat, lon, text="End")
            self.reverse_geocode_end(lat, lon)
            self.show_toast("Destination set.")

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
            label = ctk.CTkLabel(
                self.manage_frame,
                text=header,
                font=header_font,
                padx=5,
                text_color="#ffffff" if self.theme_mode == "dark" else "#000000"
            )
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
        """Cancel a booking that belongs to the current user."""
        bid_str = self.booking_id_entry.get().strip()

        # 1) fast validation
        if not bid_str.isdigit():
            self.manage_result.configure(text="❌ Enter a Booking ID.")
            return

        booking_id = int(bid_str)

        # 2) ownership / existence check
        df = self.system.view_bookings()
        row = df[df["Booking ID"] == booking_id]

        if row.empty or row.iloc[0]["User"] != self.username:
            self.manage_result.configure(text="❌ Booking ID not found.")
            return

        # 3) perform cancellation
        result = self.system.cancel_booking(booking_id)
        self.manage_result.configure(text=result)

        # 4) cleanup UI
        self.booking_id_entry.delete(0, "end")
        self.load_bookings()
        self.show_toast(result)

    def finish_booking(self):
        try:
            booking_id = int(self.booking_id_entry.get())
        except ValueError:
            self.manage_result.configure(text="❌ Invalid booking ID.")
            return

        df = self.system.view_bookings()
        booking_row = df[df["Booking ID"] == booking_id]

        if booking_row.empty or booking_row.iloc[0]["User"] != self.username:
            self.manage_result.configure(text="❌ Booking ID not found.")
            return

        # simple call – we just added this in the backend
        result = self.system.finish_booking(booking_id)

        self.manage_result.configure(text=result)
        self.booking_id_entry.delete(0, 'end')
        self.load_bookings()
        self.show_toast(result)

    def show_toast(self, message, duration=5000):
        toast = ctk.CTkLabel(self, text=message, fg_color="#323232", text_color="white", corner_radius=10, font=ctk.CTkFont(size=14))
        toast.place(relx=0.5, rely=0.05, anchor="n")

        self.after(duration, toast.destroy)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
