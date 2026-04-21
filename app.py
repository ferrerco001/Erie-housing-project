import pandas as pd
import streamlit as st
import plotly.express as px
from db_connection import supabaseManager

st.set_page_config(page_title="Housing market analysis", layout="wide")

st.title("Erie - Market analysis dashboard")
st.markdown("Invest opportunity monitor in real time")

@st.cache_data(ttl=3600)
def load_data():
    db = supabaseManager()

    response = db.supabase.table('properties').select('*').execute()
    df = pd.DataFrame(response.data)

    df = df[df['price'] > 0]

    df['latitude'] = pd.to_numeric(df['latitude'])
    df['longitude'] = pd.to_numeric(df['longitude'])

    df['property_type'] = df['property_type'].str.lower().str.replace(' ', '')

    mapping = {
        'singlefamily': 'Single Family',
        'multifamily': 'Multi-Family',
        'apartment': 'Apartment',
        'condo': 'Condo',
        'townhouse': 'Townhouse',
        'manufactured': 'Manufactured',
        'land': 'Land'
    }

    df['property_type'] = df['property_type'].map(mapping).fillna('Other')

    return df

@st.cache_data(ttl=3600)
def load_history():
    db = supabaseManager()

    response = db.supabase.table('price_history') \
    .select('price, captured_at, properties(address)') \
    .order('captured_at', desc=True) \
    .limit(5000) \
    .execute()
    df_hist = pd.DataFrame(response.data)

    df_hist['address'] = df_hist['properties'].apply(lambda x: x['address'])
    df_hist['captured_at'] = pd.to_datetime(df_hist['captured_at'])

    return df_hist

df = load_data()

st.sidebar.header("Filters")

listing_filter = st.sidebar.multiselect("Type", options=df['listing_type'].unique(),
                                        default=df['listing_type'].unique())

df_temp = df[df['listing_type'].isin(listing_filter)] if listing_filter else df

min_price = df_temp['price'].min()
max_price = df_temp['price'].max()

price_range = st.sidebar.slider("Range of price", min_value= min_price,
                                max_value=max_price, value=(min_price, max_price))

bedrooms_filter = st.sidebar.number_input('Bedrooms', step=1)
bathrooms_filter = st.sidebar.number_input('Bathrooms', step=1)

st.sidebar.write("---")
st.sidebar.subheader("Property type")

unique_types = sorted(df['property_type'].unique().tolist())

if 'selected_types' not in st.session_state or not isinstance(st.session_state.selected_types, list):
    st.session_state.selected_types = unique_types.copy()

col_all, col_clear = st.sidebar.columns(2)
if col_all.button("Select All", use_container_width=True):
    st.session_state.selected_types = unique_types.copy()
if col_clear.button("Clear All", use_container_width=True):
    st.session_state.selected_types = []

cols = st.sidebar.columns(2)
for i, p_type in enumerate(unique_types):
    col = cols[i % 2]

    is_selected = p_type in st.session_state.selected_types

    style = "primary" if is_selected else "secondary"

    if col.button(p_type, key=f"btn_{p_type}", type=style, use_container_width=True):
        if is_selected:
            st.session_state.selected_types.remove(p_type)
        else:
            st.session_state.selected_types.append(p_type)
        st.rerun()

df_filtered = df[(df['listing_type'].isin(listing_filter)) &
                 (df['price'].between(price_range[0], price_range[1])) &
                 (df['bedrooms'] >= bedrooms_filter) &
                 (df['bathrooms'] >= bathrooms_filter)]

df_filtered = df_filtered[df_filtered['property_type'].isin(st.session_state.selected_types)]


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Market analysis", "Interactive map", "Data explorer", "Oportunity searcher", "Price evolution"])

with tab1:

    st.subheader("General statistics for Erie")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Properties total: ", len(df_filtered))

    with col2:
        avg_price_sale = round(df[df['listing_type'] == 'Sale']['price'].mean(), 2)
        st.metric("Average price of sale", f"${avg_price_sale:.0f}")

    with col3:

        avg_price_rent = round(df[df['listing_type'] == 'Rent']['price'].mean(), 2)
        st.metric("Average price of rent", f"${avg_price_rent:.0f}")

    st.subheader("Properties by zipcode")
    zip_chart = px.bar(df_filtered['zip_code'].value_counts(), labels={'value' : 'amount', 'index' : 'zip_code'})
    st.plotly_chart(zip_chart, use_container_width=True)



with tab2:
    st.subheader("Location of properties")

    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])

    if not df_map.empty:
        st.map(df_map[['latitude', 'longitude']])
    else:
        st.warning("No coordinates available")

with tab3:
    st.subheader("Properties explorer")

    st.dataframe(df_filtered[['address', 'zip_code', 'price', 'bathrooms', 'bedrooms', 'listing_type']], use_container_width=True)


with tab4:
    st.subheader("Oportunity searcher")

    option = st.selectbox("Select the zipcode: ", options=sorted(df['zip_code'].unique()))

    avg_in_zipcode_rent = round(df[(df['zip_code'] == option) & (df['listing_type'] == 'Rent')]['price'].mean(), 2)
    avg_in_zipcode_sale = round(df[(df['zip_code'] == option) & (df['listing_type'] == 'Sale')]['price'].mean(), 2)

    col1, col2 = st.columns(2)

    with col1:

        st.metric("Average price of sale", f"${avg_in_zipcode_sale:.0f}")

        opportunities_sale = df[(df['price'] < avg_in_zipcode_sale) & (df['listing_type'] == 'Sale') & (df['zip_code'] == option)]


        st.dataframe(opportunities_sale[['address', 'bedrooms', 'bathrooms', 'price']].sort_values('price').head(5))

    with col2:

        st.metric("Average price of rent", f"${avg_in_zipcode_rent:.0f}")

        opportunities_rent = df[(df['price'] < avg_in_zipcode_rent) & (df['listing_type'] == 'Rent') & (df['zip_code'] == option)]

        st.dataframe(opportunities_rent[['address', 'bedrooms', 'bathrooms', 'price']].sort_values('price').head(5))


with tab5:
    st.subheader("Properties price trends")

    df_history = load_history()
    st.write(f"Última fecha detectada en el historial: {df_history['captured_at'].max()}")

    selected_address = st.selectbox("Search address to see history: ", options=df_history['address'].unique())

    property_history = df_history[df_history['address'] == selected_address].sort_values('captured_at')

    if len(property_history) > 1:
        fig = px.line(property_history, x='captured_at', y='price',
                      title=f"Price history for {selected_address}",
                      markers=True, labels={'captured_at': 'Date', 'price' : 'Price ($)'})
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("This property only has one price record yet. Trends will appear as we collect more data")
