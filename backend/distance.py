import csv
from geopy.distance import distance as geopy_distance

# Dictionary to hold street -> (latitude, longitude)
class StreetCoordinates:
    
    street_coords = {}  # Class variable to store data once

    def __init__(self):
        if not StreetCoordinates.street_coords:  # Load only once
            with open('csv_files/coordinates.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    street = row['Street'].strip()
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    StreetCoordinates.street_coords[street] = (lat, lon)

    @classmethod
    def calculate_distance(cls, street1, street2):
        if street1 not in cls.street_coords or street2 not in cls.street_coords:
            raise ValueError("One or both streets not found in the data.")
        
        coord1 = cls.street_coords[street1]
        coord2 = cls.street_coords[street2]
        return geopy_distance(coord1, coord2).miles

# # Example usage,
# # delete for integration
# distance_instance = StreetCoordinates()  # Initialize once to load data
# mile = distance_instance.calculate_distance("Pureza Street", "32nd Street")
# print(f"Distance: {mile:.2f} miles")
# # Delete the example usage for integration into a larger application

