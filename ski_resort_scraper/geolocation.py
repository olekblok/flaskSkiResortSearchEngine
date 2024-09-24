from geopy.geocoders import Nominatim


class GeoLocator:
    def __init__(self, user_agent="http"):
        self.geolocator = Nominatim(user_agent=user_agent)

    def get_coordinates(self, city: str, country: str):
        """
        Get coordinates (latitude, longitude) for a given city and country.
        :param city: city for which to get coordinates
        :param country: country for which to get coordinates
        :return: latitude and longitude for given city in given country
        """
        try:
            location = self.geolocator.geocode(f"{city}, {country}")
            if location:
                return location.latitude, location.longitude
            return None, None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None, None
