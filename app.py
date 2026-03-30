import pandas as pd
import streamlit as st
import plotly.express as px
from db_connection import supabaseManager
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="Housing market analysis", layout="wide")

st.title("Erie - Market analysis dashboard")
st.markdown("Invest opportunity monitor in real time")

@st.cache_data
def load_data():
    db = supabaseManager()

    response = db.supabase.table('properties').select('*').execute()
    df = pd.DataFrame(response.data)

    df = df[df['price'] > 0]

    df['latitude'] = pd.to_numeric(df['latitude'])
    df['longitude'] = pd.to_numeric(df['longitude'])

    return df

@st.cache_data
def get_coords(addresses):
    geolocator = Nominatim(user_agent="erie_housing_app")
    coords = []

    for addr in addresses[:20]:
        try:
            location = geolocator.geocode(f"{addr}, Erie, PA")
            if location:
                coords.append({"lat": location.latitude, "lon": location.longitude})
            time.sleep(1)
        except:
            continue
    return pd.DataFrame(coords)



df = load_data()

st.sidebar.header("Filters")

listing_filter = st.sidebar.multiselect("Type", options=df['listing_type'].unique(),
                                        default=df['listing_type'].unique())

min_price = int(df['price'].min())
max_price = df['price'].max()

price_range = st.sidebar.slider("Range of price", min_value= min_price,
                                max_value=max_price, value=(min_price, max_price))

df_filtered = df[(df['listing_type'].isin(listing_filter)) &
                 (df['price'].between(price_range[0], price_range[1]))]


tab1, tab2, tab3 = st.tabs(["Market analysis", "Interactive map", "Data explorer"])

with tab1:

    st.subheader("Estadísticas Generales de Erie")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Properties total: ", len(df_filtered))

    with col2:
        avg_price_sale = df[df['listing_type'] == 'Sale']['price'].mean()
        st.metric("Average price of sale: ", avg_price_sale)

    with col3:

        avg_price_rent = df[df['listing_type'] == 'Rent']['price'].mean()
        st.metric("Average price of rent: ", avg_price_rent)

    st.subheader("Properties by zipcode")
    zip_chart = px.bar(df_filtered['zip_code'].value_counts(), labels={'value' : 'amount', 'index' : 'zip_code'})
    st.plotly_chart(zip_chart, use_container_width=True)



with tab2:
    st.subheader("Locatoin of properties")

    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])

    if not df_map.empty:
        st.map(df_map[['latitude', 'longitude']])
    else:
        st.warning("No coordinates available")

with tab3:
    st.subheader("Properties explorer")

    st.dataframe(df_filtered[['address', 'zip_code', 'price', 'bathrooms', 'bedrooms', 'listing_type']], use_container_width=True)
