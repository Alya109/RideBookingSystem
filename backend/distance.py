from geopy.distance import distance as geopy_distance

class StreetCoordinates:
    """Handles distance calculation based purely on coordinates (no CSV)."""

    @classmethod
    def calculate_distance_from_coords(cls, coord1, coord2):
        if not coord1 or not coord2:
            raise ValueError("Both coordinates must be provided.")
        return geopy_distance(coord1, coord2).miles
