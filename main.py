from scraper_engine import ErieDataClient
from processor import DataProcessor
from db_connection import supabaseManager
from datetime  import datetime

if __name__ == '__main__':

    today_date = datetime.now().strftime("%Y-%m-%d")

    client = ErieDataClient()
    processor = DataProcessor()

    raw_data = client.get_all_data()

    clean_sales = processor.process_zillow(raw_data.get('sales', []))
    clean_rents = processor.process_rentCast(raw_data.get('rentals', []))

    clean_data = clean_rents + clean_sales

    if clean_data:
        db = supabaseManager()

        db.insertProperties(clean_data)
        id_map = db.get_id_mapping()

        history_price_data = []

        seen_properties = set()

        for p in clean_data:

            addr = p["address"]
            z_id = p["zillow_id"]
            internal_id = id_map.get(p["zillow_id"])

            if internal_id and internal_id not in seen_properties:
                history_price_data.append({
                    "property_id": internal_id,
                    "price": p["price"],
                    "listing_type": p["listing_type"],
                    "captured_at" : today_date
                })

                seen_properties.add(addr)

        if history_price_data:
            db.insertPriceHistory(history_price_data)
