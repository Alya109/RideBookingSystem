import csv
import math

# Dictionary to hold street -> (latitude, longitude)
class StreetCoordinates:
    
    street_coords = {}  # Class variable to store data once

    def __init__(self):
        if not StreetCoordinates.street_coords:  # Load only once
            with open('coordinates.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    street = row['Street'].strip()
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    StreetCoordinates.street_coords[street] = (lat, lon)

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 3958.8  # Radius of the Earth in miles
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @classmethod
    def calculate_distance(cls, street1, street2):
        if street1 not in cls.street_coords or street2 not in cls.street_coords:
            raise ValueError("One or both streets not found in the data.")
        
        lat1, lon1 = cls.street_coords[street1]
        lat2, lon2 = cls.street_coords[street2]
        return cls.haversine(lat1, lon1, lat2, lon2)

# Example usage,
# delete for integration
StreetCoordinates()  # Initialize once to load data
distance = StreetCoordinates.calculate_distance("Kalayaan Avenue", "32nd Street")
print(f"Distance: {distance:.2f} miles")

