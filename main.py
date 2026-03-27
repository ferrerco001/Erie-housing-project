from scraper_engine import ErieDataClient
from processor import DataProcessor

if __name__ == '__main__':
    client = ErieDataClient()
    processor = DataProcessor()

    raw_data = ErieDataClient().get_all_data()

    clean_sales = processor.process_zillow(raw_data.get('sales', []))
    clean_rents = processor.process_rentCast(raw_data.get('rentals', []))


    print(f" Validate sales: {len(clean_sales)}")
    print(f" Validate rents: {len(clean_rents)}")
