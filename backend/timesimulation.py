import random

vehicle_speeds = {
    "Motorcycle": 40,     # miles/hour
    "Taxi": 35,
    "Car": 38,
    "Electric Car": 34,
    "Van": 30
}

def simulate_time(distance, vehicle_type):
    
    speed = vehicle_speeds.get(vehicle_type, 30)  # Default speed if not found
    eta_minutes = (distance / speed)  * 60 # time in hours
    
    simulated_time = random.randint(int(eta_minutes * 0.9), int(eta_minutes * 1.1))
    return simulated_time

