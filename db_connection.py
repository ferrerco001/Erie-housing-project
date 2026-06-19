import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

class supabaseManager:
    def __init__(self):
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_API_KEY")

        if not url or not key:
            print("Credentials not found in github")
            print(f"DEBUG: URL presente: {bool(url)}, Key presente: {bool(key)}")

            self.supabase = None
            return

        try:
            self.supabase: Client = create_client(url, key)
        except Exception as e:
            print(f"Error connecting to supabase: {e}")
            self.supabase = None

    def getOldSaleID(self, limit = 30):
        if not self.supabase:
            return[]
        try:
            response = (
                self.supabase.table("properties")
                .select("zillow_id")
                .eq("listing_type", "Sale")
                .order("updated_at", nullsfirst=True)
                .limit(limit)
                .execute()
            )
            return [item['zillow_id'] for item in response.data]
        except Exception as e:
            print(f"Error fetching old sales {e}")
            return []

    def getOldRentalID(self, limit = 30):

        if not self.supabase:
            return []
        try:
            response = (
                self.supabase.table("properties")
                .select("zillow_id")
                .eq("listing_type", "Rent")
                .order("updated_at", nullsfirst=True)
                .limit(limit)
                .execute()
            )
            return [item['zillow_id'] for item in response.data]
        except Exception as e:
            print(f"Error fetching old rental IDs: {e}")
            return []

    def insertProperties(self, properties):

        if not properties:
            return

        try:

            now_str = datetime.now().isoformat()
            for p in properties:
                p["updated_at"] = now_str

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
        if not self.supabase:
            return {}
        try:
            response = self.supabase.table("properties").select("id, zillow_id").execute()
            return {item['zillow_id']: item['id'] for item in response.data}

        except Exception as e:
            print(f" Error getting IDs: {e}")
            return {}

    def getPropertiesWithoutCoordinates(self, limit=20):
        if not self.supabase:
            return []
        try:
            response = (
                self.supabase.table("properties")
                .select("id, address")
                .is_("latitude", "null")
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching properties without coordinates: {e}")
            return []

    def updatePropertyCoordinates(self, property_id, lat, lon):
        """Actualiza la latitud y longitud de una propiedad específica en Supabase."""
        if not self.supabase:
            return
        try:
            self.supabase.table("properties").update({
                "latitude": lat,
                "longitude": lon
            }).eq("id", property_id).execute()
        except Exception as e:
            print(f"Error updating coordinates for property {property_id}: {e}")
