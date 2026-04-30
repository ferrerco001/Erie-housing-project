#  Erie Housing Insight: End-to-End Data Pipeline & Analytics

[![Streamlit App](https://streamlit.io)](https://erie-housing-project-4pazlfff8hh7wbswlng2bd.streamlit.app/)

A **data engineering pipeline** designed to monitor and analyze the real estate market in Erie, PA. This system automates data extraction from multiple APIs, cleanses and normalizes records, maintains a historical price database, and visualizes investment opportunities through an interactive dashboard.

![Dashboard Preview](assets/dashboard_map.png)

##  Key Features

*   **Automated Weekly ETL:** Fully automated extraction cycles using **GitHub Actions**, ensuring a "set-and-forget" data update mechanism.
*   **Price History Tracking:** Tracks price fluctuations over time for each property, enabling time-series market analysis.
*   **Data Integrity & Validation:** Data cleaning using **Pydantic** models to ensure type safety and schema consistency before database ingestion.
*   **Investment Opportunity Engine:** A dynamic tool that identifies properties listed below the local ZIP code average, helping investors find high-value deals.

###  Data-Driven Insights
![Investment Opportunities](assets/opportunities.png)

##  Tech Stack

*   **Language:** Python 3.11+
*   **Data Ingestion:** RapidAPI (Zillow Engine) & RentCast API.
*   **Database:** PostgreSQL (Hosted on **Supabase**).
*   **Data Processing:** Pandas, Pydantic, Geopy (Nominatim).
*   **Dashboarding:** **Streamlit** & Plotly Express.
*   **DevOps/CI-CD:** GitHub Actions & Streamlit Cloud.

##  System Architecture

1.  **Ingestion Layer:** Fetches raw sales and rental data via REST APIs.
2.  **Processing Layer:** Cleanses addresses and handles coordinate mapping. Normalizes street addresses to serve as a reliable deduplication key across different data providers.
3.  **Persistence Layer:**  Executes `upsert` operations on the master property table and `insert` operations on the historical price table, enforcing data integrity through Python-level validation.
4.  **Presentation Layer:** A real-time web application that serves filtered insights and trend visualizations.

##   Challenges & Solutions

*   **Deduplication Logic:** Implemented address-based normalization to prevent duplicate records in cases where the same physical property might be listed across different providers or categories (Sale/Rent) during the same execution cycle.

*   **Temporal Consistency:** Standardized date formats to ISO8601, resolving conflicts between cloud database timestamps and Pandas datetime objects.

*   **Geocoding Optimization:** Developed a custom address-cleaning regex to improve coordinate accuracy and handled API rate limits using a controlled sleep mechanism.

### 📈 Historical Tracking
![Price Trends](assets/trends.png)

##  Project Structure

```text
├── .github/workflows/       # CI/CD Pipeline (GitHub Actions)
├── app.py                   # Streamlit Dashboard
├── main.py                  # ETL Orchestrator
├── db_connection.py         # Data Access Layer (Supabase)
├── processor.py             # Data Cleaning & Transformation
├── scraper_engine.py        # API Ingestion Logic
├── models.py                # Pydantic Data Models
├── requirements.txt         # Project Dependencies
└── README.md
```

##  Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ferrerco001/Erie-housing-project.git
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables:** Create a `.env` file with the following:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_API_KEY=your_supabase_key
   ZILLOW_API_KEY=your_rapidapi_key
   RENTCAST_API_KEY=your_rentcast_key
   ```
4. **Run the Application:**
   *   To trigger the pipeline: `python main.py`
   *   To launch the dashboard: `streamlit run app.py`

---
Developed by Pau Ferrer Collado
