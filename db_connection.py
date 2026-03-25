import os
from dotenv import load_dotenv
from supabase import create_client

class ConnectionDB:
    def __init__(self):
        load_dotenv()

    def connectionSupabase(self):
        url = os.getenv('SUPABASE_URL')
        api_key = os.getenv('SUPABASE_API_KEY')

        supabase = create_client(url, api_key)

        return supabase

try:
    test = ConnectionDB()
    client = test.connectionSupabase()
    print(test.connectionSupabase())

    response = client.table('properties').select('id').limit(1).execute()
    print('Successful connection')

except Exception as e:
    print(f'Error {e}')
