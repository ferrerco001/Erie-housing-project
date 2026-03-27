from models import PropertyModel

class DataProcessor:

    @staticmethod
    def process_zillow(raw_sales):

        clean_properties = []

        for p in raw_sales:

            property_data = p.get('property', {})

            try:
                data = {
                    "zillow_id" : str(property_data.get('zpid')),
                    "address" : str(property_data.get('address', {}).get('streetAddress')),
                    "zip_code" : str(property_data.get('address', {}).get('zipcode')),
                    "price" : int(property_data.get('price', {}).get('value', 0)),
                    "sqft" : int(property_data.get('livingArea', 0)),
                    "bedrooms" : float(property_data.get('bedrooms', 0)),
                    "bathrooms" : float(property_data.get('bathrooms', 0)),
                    "property_type" : str(property_data.get('propertyType', 'Unknown')),
                    "listing_type" : 'Sale'
                }

                clean_properties.append(PropertyModel(**data).model_dump())
            except Exception as e:
                print(f"Skipping property: {e}")
        return clean_properties

    @staticmethod
    def process_rentCast(raw_rents):

        clean_properties = []

        for p in raw_rents:

            try:
                data = {
                    "zillow_id" : str(p.get('id')),
                    "address" : str(p.get('addressLine1')),
                    "zip_code" : str(p.get('zipCode')),
                    "price" : int(p.get('price', 0)),
                    "sqft" : int(p.get('squareFootage', 0)),
                    "bedrooms" : float(p.get('bedrooms', 0)),
                    "bathrooms" : float(p.get('bathrooms', 0)),
                    "property_type" : str(p.get('propertyType', 'Unknown')),
                    "listing_type" : 'Rent'
                }

                clean_properties.append(PropertyModel(**data).model_dump())

            except Exception as e:
                print(f"Skipping house: {e}")

        return clean_properties
