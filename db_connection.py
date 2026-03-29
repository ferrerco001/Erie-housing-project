import os
from dotenv import load_dotenv
from supabase import create_client, Client

class supabaseManager:
    def __init__(self):
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_API_KEY")

        if not url or not key:
            print("Credentials not found in github")
            print(f"DEBUG: URL presente: {bool(url)}, Key presente: {bool(key)}")
            # No intentamos crear el cliente si no hay datos
            self.supabase = None
            return

        try:
            self.supabase: Client = create_client(url, key)
        except Exception as e:
            print(f"Error connecting to supabase: {e}")
            self.supabase = None

    def insertProperties(self, properties):

        if not properties:
            return

        try:
            response = self.supabase.table("properties").upsert(properties, on_conflict="zillow_id").execute()

            return response

        except Exception as e:
            print(f"Error in the upsert: {e}")

    def insertPriceHistory(self, properties_prices):

        if not properties_prices:
            return

        try:
            self.supabase.table('price_history').insert(properties_prices).execute()

        except Exception as e:
            print(f"Error inserting in pricce_history {e}")

    def get_id_mapping(self):

        try:
            response = self.supabase.table("properties").select("id, zillow_id").execute()
            return {item['zillow_id']: item['id'] for item in response.data}

        except Exception as e:
            print(f" Error getting IDs: {e}")
            return {}
