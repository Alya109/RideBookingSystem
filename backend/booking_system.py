import pandas as pd
import datetime
from backend.distance import StreetCoordinates
from backend.timesimulation import simulate_time
from backend.vehicle import Motorcycle, Taxi, Car, ElectricCar, Van


class Booking:
    booking_id_counter = 1000

    def __init__(self, user, vehicle_type, start_loc, end_loc, distance, time) -> None:
        self.booking_id = Booking.booking_id_counter
        Booking.booking_id_counter += 1

        self.status = "Active"
        self.user = user
        self.vehicle_type = vehicle_type
        self.start_loc = start_loc  # already readable location string
        self.end_loc = end_loc
        self.date = datetime.datetime.now().strftime("%m-%d-%Y")
        self.distance = distance   
        self.time = time           

        vehicle = self.get_vehicle()
        self.total_cost = vehicle.calculate_cost(self.distance, self.time)

    def get_vehicle(self):
        return {
            "Motorcycle": Motorcycle(),
            "Taxi": Taxi(),
            "Car": Car(),
            "Electric Car": ElectricCar(),
            "Van": Van()
        }.get(self.vehicle_type, Car())

    def to_dict(self):
        return {
            "Booking ID": self.booking_id,
            "Status": self.status,
            "User": self.user,
            "Vehicle Type": self.vehicle_type,
            "From": self.start_loc,
            "To": self.end_loc,
            "Date": self.date,
            "Distance": round(self.distance, 2),
            "Total Cost": f"P {self.total_cost:.2f}"
        }

class BookingSystem:
    def __init__(self, file_path="csv_files/bookings.csv"):
        self.file_path = file_path
        self.bookings = self._load_from_file()
        StreetCoordinates()
        
    def _load_from_file(self):
        try:
            df = pd.read_csv(self.file_path)
            Booking.booking_id_counter = df['Booking ID'].max() + 1 if not df.empty else 1000
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=[
                "Booking ID",
                "Status", 
                "User", 
                "Vehicle Type", 
                "From", 
                "To", 
                "Date", 
                "Distance", 
                "Total Cost"
            ])
            
    def _save_to_file(self):
        self.bookings.to_csv(self.file_path, index=False)
        
    def book_ride(self, user, vehicle_type, start_loc, end_loc, distance, time):
        new_booking = Booking(user, vehicle_type, start_loc, end_loc, distance, time)
        self.bookings = pd.concat([self.bookings, pd.DataFrame([new_booking.to_dict()])], ignore_index=True)
        self._save_to_file()
        return new_booking.booking_id

    def view_bookings(self):
        return self.bookings
    
    def cancel_booking(self, booking_id: int) -> str:
        """Set status to Cancelled only if it is currently Active."""
        mask = self.bookings["Booking ID"] == booking_id
        if not mask.any():
            return "❌ Booking ID not found."

        current_status = self.bookings.loc[mask, "Status"].iloc[0]

        if current_status == "Finished":
            return "❌ Ride is already finished. You can’t cancel it."
        if current_status == "Cancelled":
            return "ℹ️ Ride is already cancelled."

        # proceed with normal cancellation
        self.bookings.loc[mask, "Status"] = "Cancelled"
        self._save_to_file()
        return f"✅ Booking ID {booking_id} has been cancelled."

    def finish_booking(self, booking_id: int) -> str:
        """Mark a ride Finished and write the CSV back to disk, unless already Cancelled."""
        idx = self.bookings[self.bookings["Booking ID"] == booking_id].index
        if idx.empty:
            return "❌ Booking ID not found."

        # ⛔ Prevent marking a Cancelled ride as Finished
        current_status = self.bookings.loc[idx[0], "Status"]
        if current_status == "Cancelled":
            return "❌ Cannot finish a cancelled booking."

        self.bookings.loc[idx, "Status"] = "Finished"
        self._save_to_file()
        return "✅ Booking marked as finished."

    def update_status(self, booking_id: int, new_status: str) -> str:
        """Generic status setter (optional, but nice to have)."""
        idx = self.bookings[self.bookings["Booking ID"] == booking_id].index
        if idx.empty:
            return "❌ Booking ID not found."

        self.bookings.loc[idx, "Status"] = new_status
        self._save_to_file()                       # ← same fix here
        return f"✅ Booking set to {new_status}."