import datetime
from vehicle import Motorcycle, Taxi, Car, ElectricCar, Van
from distance import calculate_distance

class Booking:
    booking_id_counter = 1000
    
    def __init__(self, user, vehicle_type, start_loc, end_loc, time=0) -> None:
        self.booking_id = Booking.booking_id_counter
        Booking.booking_id_counter += 1
        
        self.status = "Active"
        self.user = user
        self.vehicle_type = vehicle_type
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.date = datetime.datetime.now().strftime("%m-%d-%Y")
        self.distance = # distance calculation logic here
        self.time = # time calculation logic here
        
        vehicle = self.get_vehicle()
        self.total_cost = vehicle.calculate_cost()
        
    def cancel_booking(self):
        self.status = "Cancelled"
        