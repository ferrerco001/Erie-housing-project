import os
import requests
from dotenv import load_dotenv

class ErieDataClient:
    def __init__(self):
        load_dotenv()

        self.zillow_key = os.getenv("ZILLOW_API_KEY")
        self.zillow_host = "zllw-working-api.p.rapidapi.com"

        self.rentcast_key = os.getenv("RENTCAST_API_KEY")
        self.rentcast_url = "https://api.rentcast.io"

    def fetchZillowSalesNew(self):
        url = f"https://{self.zillow_host}/search/byaddress"

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

                    page_props = data

                    if not page_props:
                        break


                    all_pages_props.extend(data.get('searchResults', []))


                    current_page += 1
                else:
                    print(f" Error {response.status_code} en la página {current_page}")
                    break

            except Exception as e:
                print(f'Exception en página {current_page}: {e}')
                break


        return all_pages_props

    def fetchZillowSaleById(self, zpid):

        url = f"https://{self.zillow_host}/property"

        headers = {
            "x-rapidapi-key": self.zillow_key,
            "x-rapidapi-host": self.zillow_host
        }

        query = {"zpid": str(zpid)}

        try:
            response = requests.get(url, headers=headers, params=query, timeout=15)
            if response.status_code == 200:

                data = response.json()
                return {"property": data} if isinstance(data, dict) else data

            print(f"Error Zillow ID {zpid}: {response.status_code}")

            return None

        except Exception as e:
            print(f'Exception Zillow ID {zpid}: {e}')
            return None

    def fetchRentcastNew(self):
        url = "https://api.rentcast.io/v1/listings/rental/long-term"

        query = {"city" : "Erie", "state" : "PA", "limit": 30}

        headers = {
            "accept": "application/json",
            "X-Api-Key": self.rentcast_key
        }

        try:
            response = requests.get(url, headers=headers, params=query, timeout=15)
            if response.status_code == 200:
                print('success')
                return response.json()
            else:
                print(response.status_code)
                return []
        except Exception as e:
            print(f'exception {e}')

    def fetchRentcastByID(self, property_id):

        url = f"{self.rentcast_url}/v1/listings/rental/long-term/{property_id}"

        headers = {
            "accept": "application/json",
            "X-Api-Key": self.rentcast_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                return response.json()

            print(f"Error RentCast ID {property_id}: {response.status_code}")
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
