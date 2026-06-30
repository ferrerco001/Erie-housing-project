import os
import requests
from urllib.parse import unquote
from dotenv import load_dotenv

class ErieDataClient:
    def __init__(self):
        load_dotenv()
        # Leemos únicamente las llaves secretas del archivo .env
        self.zillow_key = os.getenv("ZILLOW_API_KEY")
        self.rentcast_key = os.getenv("RENTCAST_API_KEY")

        # Fijamos los hosts estables directamente para evitar errores de concatenación en el .env
        self.zillow_host = "zllw-working-api.p.rapidapi.com"

    def fetchZillowSalesNew(self):
        # Fijamos la URL completa oficial directamente en el string
        url = "https://{self.zillow_host}/search/byaddress"
        all_pages_props = []
        MAX_PAGES = 3
        current_page = 1
        headers = {
            "x-rapidapi-key": self.zillow_key,
            "x-rapidapi-host": self.zillow_host
        }
        while current_page <= MAX_PAGES:
            query = {
                "location": "Erie, PA",
                "status": "forSale",
                "page": str(current_page)
            }
            try:
                response = requests.get(url=url, headers=headers, params=query, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    searchResults = data.get('searchResults', []) if isinstance(data, dict) else data
                    if not searchResults:
                        break
                    all_pages_props.extend(searchResults)
                    current_page += 1
                else:
                    print(f" Error Zillow New {response.status_code} en la página {current_page}")
                    break
            except Exception as e:
                print(f'Exception Zillow New en página {current_page}: {e}')
                break
        return all_pages_props

    def fetchZillowSaleById(self, zpid):
        # Fijamos la URL completa oficial directamente en el string
        url = f"https://{self.zillow_host}/search/byaddress"
        headers = {
            "x-rapidapi-key": self.zillow_key,
            "x-rapidapi-host": self.zillow_host
        }
        query = {"zpid": str(zpid)}
        try:
            response = requests.get(url=url, headers=headers, params=query, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return {"property": data} if isinstance(data, dict) else data

            # Si da 404 porque la casa caducó, pasamos de largo de forma segura
            if response.status_code == 404:
                return None

            print(f"Error Zillow ID {zpid}: {response.status_code}")
            return None
        except Exception as e:
            print(f'Exception Zillow ID {zpid}: {e}')
            return None

    def fetchRentcastNew(self):
        # Fijamos el endpoint completo oficial directo de RentCast
        url = "https://api.rentcast.io/v1/listings/rental/long-term"
        query = {"city" : "Erie", "state" : "PA", "limit": 30}
        headers = {
            "accept": "application/json",
            "X-Api-Key": self.rentcast_key
        }
        try:
            response = requests.get(url, headers=headers, params=query, timeout=15)
            if response.status_code == 200:
                return response.json()
            print(f"Error RentCast New: {response.status_code}")
            return []
        except Exception as e:
            print(f'Exception RentCast New: {e}')
            return []

    def fetchRentcastByID(self, property_id):
        # Fijamos el endpoint completo oficial directo de RentCast
        url = f"{self.rentcast_url}/v1/listings/rental/long-term/{property_id}"

        # Decodificamos y limpiamos guiones/comas de la base de datos
        decoded_address = unquote(str(property_id))
        clean_address = decoded_address.replace('-', ' ').replace(',', ' ')

        query = {"address": clean_address.strip(), "limit": 1}
        headers = {
            "accept": "application/json",
            "X-Api-Key": self.rentcast_key
        }
        try:
            response = requests.get(url, headers=headers, params=query, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) and len(data) > 0 else None
            print(f"Error RentCast Address Lookup {property_id}: {response.status_code}")
            return None
        except Exception as e:
            print(f'Exception RentCast ID {property_id}: {e}')
            return None

    def get_all_data(self, old_sale_ids=None, old_rental_ids=None):
        sales_data = self.fetchZillowSalesNew()
        rentals_data = self.fetchRentcastNew()

        if old_sale_ids:
            for zpid in old_sale_ids[:30]:
                updated_sale = self.fetchZillowSaleById(zpid)
                if updated_sale:
                    sales_data.append(updated_sale)

        if old_rental_ids:
            for pid in old_rental_ids[:30]:
                updated_rental = self.fetchRentcastByID(pid)
                if updated_rental:
                    rentals_data.append(updated_rental)

        return {
            "sales" : sales_data,
            "rentals" : rentals_data
        }

if __name__ == '__main__':
    client = ErieDataClient()
    data = client.get_all_data()
