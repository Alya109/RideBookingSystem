# main.py
from backend.booking_system import BookingSystem

def main():
    system = BookingSystem()

    print("=== SadRide Booking System ===")
    user = input("Enter your name: ").strip()
    print("Available vehicle options:")
    for name in system.get_vehicle_names():
        print("-", name)

    vehicle = input("Enter vehicle name exactly: ").strip()
    start = input("Enter start location: ").strip()
    end = input("Enter end location: ").strip()

    group_size = 1
    if "Van" in vehicle:
        group_size = int(input("Enter group size: "))

    try:
        booking_id = system.book_ride(user, vehicle, start, end, group_size)
        print(f"Booking successful! ID: {booking_id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
