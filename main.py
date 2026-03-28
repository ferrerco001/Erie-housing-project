from scraper_engine import ErieDataClient
from processor import DataProcessor
from db_connection import supabaseManager

if __name__ == '__main__':
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

        for p in clean_data:

            internal_id = id_map.get(p["zillow_id"])

            if internal_id:
                history_price_data.append({
                    "property_id": internal_id,
                    "price": p["price"],
                    "listing_type": p["listing_type"]
                })

        if history_price_data:
            db.insertPriceHistory(history_price_data)
