from vehicle import Motorcycle, Taxi, Car, ElectricCar, Van

class Booking:
    booking_id_counter = 1000
    def __init__(self, vehicle_type, user, pickoff_location, dropoff_location, fare):
        self.booking_id = Booking.booking_id_counter
        Booking.booking_id_counter += 1
        self.vehicle_type = vehicle_type
        self.user = user
        self.pickoff_location = pickoff_location
        self.dropoff_location = dropoff_location
        self.fare = fare
