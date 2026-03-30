from models import PropertyModel
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import time

class DataProcessor:

    def __init__(self):
        self.geolocator = Nominatim(user_agent="erie-housing-pipeline")

    def get_coordinates(self, address):

        try:
            location = self.geolocator.geocode(f"{address}, Erie, PA", timeout=10)
            if location:
                return location.latitude, location.longitude

        except GeopyError as e:
            print(f"Error getting location {e}")

        return None, None

    def process_zillow(self, raw_sales):

        clean_properties = []

        for p in raw_sales:

            property_data = p.get('property', {})

            try:

                beds = float(property_data.get('bedrooms', 0))
                addr = str(property_data.get('address', {}).get('streetAddress', '')).lower()

                if beds > 10 or "investment" in addr or "package" in addr:
                    continue

                lat, lon = self.get_coordinates(addr)
                time.sleep(1)

                data = {
                    "zillow_id" : str(property_data.get('zpid')),
                    "address" : str(property_data.get('address', {}).get('streetAddress')),
                    "zip_code" : str(property_data.get('address', {}).get('zipcode')),
                    "price" : int(property_data.get('price', {}).get('value', 0)),
                    "sqft" : int(property_data.get('livingArea', 0)),
                    "bedrooms" : float(property_data.get('bedrooms', 0)),
                    "bathrooms" : float(property_data.get('bathrooms', 0)),
                    "property_type" : str(property_data.get('propertyType', 'Unknown')),
                    "listing_type" : 'Sale',
                    "latitude" : lat,
                    "longitude" : lon
                }

                clean_properties.append(PropertyModel(**data).model_dump())
            except Exception as e:
                print(f"Skipping property: {e}")
        return clean_properties

    def process_rentCast(self, raw_rents):

        clean_properties = []

        for p in raw_rents:

            try:
                beds = float(p.get('bedrooms', 0))
                addr = str(p.get('address', '')).lower()

                if beds > 10 or "investment" in addr or "package" in addr:
                    continue

                lat, lon = self.get_coordinates(addr)
                time.sleep(1)

                data = {
                    "zillow_id" : str(p.get('id')),
                    "address" : str(p.get('addressLine1')),
                    "zip_code" : str(p.get('zipCode')),
                    "price" : int(p.get('price', 0)),
                    "sqft" : int(p.get('squareFootage', 0)),
                    "bedrooms" : float(p.get('bedrooms', 0)),
                    "bathrooms" : float(p.get('bathrooms', 0)),
                    "property_type" : str(p.get('propertyType', 'Unknown')),
                    "listing_type" : 'Rent',
                    "latitude" : lat,
                    "longitude" : lon
                }

                clean_properties.append(PropertyModel(**data).model_dump())

            except Exception as e:
                print(f"Skipping house: {e}")

        return clean_properties
