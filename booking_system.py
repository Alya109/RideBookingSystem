import pandas as pd
from booking import Booking
from vehicle import Motorcycle, Taxi, Car, ElectricCar, Van

class BookingSystem:
    def __init__(self, file_path="csv_files/bookings.csv"):
        self.file_path = file_path
        self.bookings = self._load_from_file()
        
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
        
    def book_ride(self, user, vehicle_type, start_loc, end_loc, time=0):
        new_booking = Booking(user, vehicle_type, start_loc, end_loc, time)
        self.bookings = pd.concat([self.bookings, pd.DataFrame([new_booking.to_dict()])], ignore_index=True)
        self._save_to_file()
        return new_booking.booking_id
    
    def view_bookings(self):
        return self.bookings
    
    def cancel_booking(self, booking_id):
        mask = self.bookings['Booking ID'] == booking_id
        if not mask.any():
            return "Booking ID not found."
        self.bookings.loc[mask, 'Status'] = 'Cancelled'
        self._save_to_file()
        return f"Booking ID {booking_id} has been cancelled."
    