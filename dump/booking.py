import datetime
from backend.distance import StreetCoordinates
from backend.timesimulation import simulate_time

class Booking:
    booking_id_counter = 1000
    
    def __init__(self, user, vehicle_type, start_loc, end_loc) -> None:
        self.booking_id = Booking.booking_id_counter
        Booking.booking_id_counter += 1
        
        self.status = "Active"
        self.user = user
        self.vehicle_type = vehicle_type
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.date = datetime.datetime.now().strftime("%m-%d-%Y")
        self.distance = StreetCoordinates.calculate_distance(start_loc, end_loc)
        self.time = simulate_time(self.distance, vehicle_type)
        
        vehicle = self.get_vehicle()
        self.total_cost = vehicle.calculate_cost()
        
    def cancel_booking(self):
        self.status = "Cancelled"
    
    def to_dict(self):
        return {
            "Booking ID": self.booking_id,
            "Status": self.status,
            "User": self.user,
            "Vehicle Type": self.vehicle_type,
            "From": self.start,
            "To": self.end,
            "Date": self.date,
            "Distance": self.distance,
            "Travel time: ": f"{self.time} minutes",
            "Total Cost": f"P {self.total_cost}"
        }    