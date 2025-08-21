# app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- DATABASE CONNECTION (using SQLite for deployment) ---
DATABASE_URI = "sqlite:///food_waste.db"

try:
    engine = create_engine(DATABASE_URI)
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# --- UI LAYOUT ---
st.title("Local Food Wastage Management System")

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")
# Initialize selected_cities as an empty list to prevent NameError
selected_cities = [] 
try:
    with engine.connect() as connection:
        # Get a unique list of cities to populate the filter (no quotes)
        cities_df = pd.read_sql(text('SELECT DISTINCT City FROM Providers ORDER BY City'), connection)
        city_list = cities_df["City"].tolist()
        
        # Create a multiselect widget for cities
        selected_cities = st.sidebar.multiselect("Select City", options=city_list)
except Exception as e:
    st.sidebar.error(f"Could not load filters: {e}")


# --- SIDEBAR FOR QUERY SELECTION ---
st.sidebar.title("Analysis Options")
st.sidebar.markdown("Select a question to display the corresponding data analysis.")

# A dictionary mapping questions to SQL queries (WITHOUT double quotes)
queries = {
    "1. Providers & Receivers per City": {
        "query": 'SELECT City, COUNT(Provider_ID) AS NumberOfProviders FROM Providers GROUP BY City;',
        "chart": None
    },
    "2. Provider type contribution": {
        "query": 'SELECT Provider_Type, SUM(Quantity) AS TotalQuantity FROM Food_Listings GROUP BY Provider_Type ORDER BY TotalQuantity DESC;',
        "chart": "bar"
    },
    "3. Contact info for providers in a specific city (Example: New York)": {
        "query": "SELECT Name, Address, Contact FROM Providers WHERE City = 'New York';",
        "chart": None
    },
    "4. Receivers who claimed the most": {
        "query": '''
            SELECT R.Name, COUNT(C.Claim_ID) AS TotalClaims 
            FROM Claims C JOIN Receivers R ON C.Receiver_ID = R.Receiver_ID 
            GROUP BY R.Name ORDER BY TotalClaims DESC;
        ''',
        "chart": "bar"
    },
    "5. Total quantity of available food": {
        "query": '''
            SELECT SUM(Quantity) AS TotalAvailableQuantity
            FROM Food_Listings
            WHERE Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed');
        ''',
        "chart": None
    },
    "6. City with the most food listings": {
        "query": 'SELECT Location, COUNT(Food_ID) AS NumberOfListings FROM Food_Listings GROUP BY Location ORDER BY NumberOfListings DESC;',
        "chart": "bar"
    },
    "7. Most common food types": {
        "query": 'SELECT Food_Type, COUNT(Food_ID) AS ListingCount FROM Food_Listings GROUP BY Food_Type ORDER BY ListingCount DESC;',
        "chart": "bar"
    },
    "8. Claims per food item": {
        "query": '''
            SELECT FL.Food_Name, COUNT(C.Claim_ID) AS NumberOfClaims 
            FROM Claims AS C JOIN Food_Listings AS FL ON C.Food_ID = FL.Food_ID 
            GROUP BY FL.Food_Name ORDER BY NumberOfClaims DESC;
        ''',
        "chart": None
    },
    "9. Provider with most successful claims": {
        "query": '''
            SELECT P.Name, COUNT(C.Claim_ID) AS SuccessfulClaims 
            FROM Claims C 
            JOIN Food_Listings FL ON C.Food_ID = FL.Food_ID 
            JOIN Providers P ON FL.Provider_ID = P.Provider_ID 
            WHERE C.Status = 'Completed' 
            GROUP BY P.Name ORDER BY SuccessfulClaims DESC;
        ''',
        "chart": "bar"
    },
    "10. Percentage of claim statuses": {
        "query": '''
            SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims) AS Percentage 
            FROM Claims GROUP BY Status;
        ''',
        "chart": None
    },
    "11. Average quantity claimed per receiver": {
        "query": '''
            SELECT R.Name, AVG(FL.Quantity) AS AverageQuantityClaimed 
            FROM Claims AS C 
            JOIN Food_Listings AS FL ON C.Food_ID = FL.Food_ID 
            JOIN Receivers AS R ON C.Receiver_ID = R.Receiver_ID 
            GROUP BY R.Name;
        ''',
        "chart": None
    },
    "12. Most claimed meal type": {
        "query": '''
            SELECT FL.Meal_Type, COUNT(C.Claim_ID) AS NumberOfClaims 
            FROM Claims C JOIN Food_Listings FL ON C.Food_ID = FL.Food_ID 
            GROUP BY FL.Meal_Type ORDER BY NumberOfClaims DESC;
        ''',
        "chart": "bar"
    },
    "13. Total food donated by each provider": {
        "query": '''
            SELECT P.Name, SUM(FL.Quantity) AS TotalQuantityDonated
            FROM Food_Listings AS FL JOIN Providers AS P ON FL.Provider_ID = P.Provider_ID
            GROUP BY P.Name ORDER BY TotalQuantityDonated DESC;
        ''',
        "chart": "bar"
    }
}

option = st.sidebar.selectbox(
    "Choose a question to analyze",
    options=list(queries.keys())
)

st.header(option)

selected_query = queries[option]["query"]
chart_type = queries[option]["chart"]

try:
    with engine.connect() as connection:
        df = pd.read_sql(text(selected_query), connection)
        st.dataframe(df)
        
        if chart_type == "bar" and not df.empty:
            st.markdown("---")
            st.subheader("Chart")
            chart_df = df.set_index(df.columns[0])
            st.bar_chart(chart_df)

except Exception as e:
    st.error(f"An error occurred while executing the query: {e}")

# --- DISPLAY FILTERED DATA ---
st.header("All Food Listings")
try:
    with engine.connect() as connection:
        query = 'SELECT * FROM Food_Listings' # Removed quotes
        
        if selected_cities:
            cities_tuple = tuple(selected_cities)
            # Handle case where only one city is selected, which would create a tuple like ('New York',)
            if len(cities_tuple) == 1:
                query += f" WHERE Location = '{cities_tuple[0]}'"
            else:
                query += f' WHERE Location IN {cities_tuple}'
            
        query += ';'
        listings_df = pd.read_sql(text(query), connection)
        st.dataframe(listings_df)
except Exception as e:
    st.error(f"An error occurred while fetching listings: {e}")

# (The CRUD/Add form code would go here if you have it)
