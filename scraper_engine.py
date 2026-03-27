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

    def fetch_zillow_sales(self):
        url = f"https://{self.zillow_host}/search/byaddress"

        all_pages_props = []
        MAX_PAGES = 5
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

    def fetch_rentcast(self):
        url = "https://api.rentcast.io/v1/properties"

        query = {"city" : "Erie", "state" : "PA", "limit": 40}

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

    def get_all_data(self):

        sales_data = self.fetch_zillow_sales()
        rent_data = self.fetch_rentcast()

        return {
            "sales" : sales_data,
            "rentals" : rent_data
        }

if __name__ == '__main__':
    client = ErieDataClient()
    data = client.get_all_data()
