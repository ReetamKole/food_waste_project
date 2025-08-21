# --------------------------------------------------------------------------
# 01_setup_database.py
#
# This script is for the ONE-TIME SETUP of your PostgreSQL database.
# It populates the 'food_waste_db' with tables and data.
#
# **BEFORE YOU RUN**:
#   - Make sure your virtual environment is active in the VS Code terminal.
#   - Update the DATABASE_URI string below with your PostgreSQL password.
#   - Ensure your .csv files are in a subfolder named 'data'.
# --------------------------------------------------------------------------

import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# --- 1. DATABASE CONNECTION SETUP ---
# ACTION: Replace 'your_password' with the password you set for PostgreSQL.
# Example:
DATABASE_URI = "postgresql://postgres:][12nrmkole@localhost:5432/food_waste_db"

# Create a connection engine to the database
try:
    engine = create_engine(DATABASE_URI)
    print("✅ Connection to PostgreSQL database successful.")
except Exception as e:
    print(f"🔥 Failed to connect to the database. Error: {e}")
    sys.exit() # Exit the script if connection fails

# --- 2. SQL STATEMENTS FOR TABLE CREATION ---
# Using 'CREATE TABLE IF NOT EXISTS' makes the script safe to re-run.
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS "Providers" (
    "Provider_ID" INTEGER PRIMARY KEY,
    "Name" VARCHAR(255),
    "Type" VARCHAR(255),
    "Address" TEXT,
    "City" VARCHAR(255),
    "Contact" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "Receivers" (
    "Receiver_ID" INTEGER PRIMARY KEY,
    "Name" VARCHAR(255),
    "Type" VARCHAR(255),
    "City" VARCHAR(255),
    "Contact" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "Food_Listings" (
    "Food_ID" INTEGER PRIMARY KEY,
    "Food_Name" VARCHAR(255),
    "Quantity" INTEGER,
    "Expiry_Date" DATE,
    "Provider_ID" INTEGER,
    "Provider_Type" VARCHAR(255),
    "Location" VARCHAR(255),
    "Food_Type" VARCHAR(255),
    "Meal_Type" VARCHAR(255),
    FOREIGN KEY ("Provider_ID") REFERENCES "Providers"("Provider_ID")
);

CREATE TABLE IF NOT EXISTS "Claims" (
    "Claim_ID" INTEGER PRIMARY KEY,
    "Food_ID" INTEGER,
    "Receiver_ID" INTEGER,
    "Status" VARCHAR(255),
    "Timestamp" TIMESTAMP,
    FOREIGN KEY ("Food_ID") REFERENCES "Food_Listings"("Food_ID"),
    FOREIGN KEY ("Receiver_ID") REFERENCES "Receivers"("Receiver_ID")
);
"""

# --- 3. EXECUTE TABLE CREATION ---
try:
    with engine.connect() as connection:
        # PostgreSQL doesn't support multiple statements in one execute call with DBAPI,
        # so we split them.
        for statement in CREATE_TABLES_SQL.strip().split(';'):
            if statement.strip():
                connection.execute(text(statement))
        connection.commit() # Commit the transaction
    print("✅ Tables created successfully (or already exist).")
except Exception as e:
    print(f"🔥 An error occurred during table creation: {e}")
    sys.exit()

# --- 4. LOAD DATA FROM CSV FILES ---
# A dictionary mapping CSV filenames to their corresponding table names.
csv_to_table_map = {
    'providers_data.csv': 'Providers',
    'receivers_data.csv': 'Receivers',
    'food_listings_data.csv': 'Food_Listings',
    'claims_data.csv': 'Claims'
}

# Path to the data subfolder
data_folder = 'data'

# Loop through the map to load each CSV into its table
for csv_file, table_name in csv_to_table_map.items():
    file_path = os.path.join(data_folder, csv_file)
    try:
        print(f"🔄 Loading data from '{csv_file}' into '{table_name}' table...")
        
        df = pd.read_csv(file_path)
        
        # Use DataFrame.to_sql() to insert data. 'append' adds the data.
        df.to_sql(table_name, engine, if_exists='append', index=False)
        
        print(f"✅ Successfully loaded data into '{table_name}'.")

    except FileNotFoundError:
        print(f"🔥 Error: The file '{file_path}' was not found. Please check the path.")
    except Exception as e:
        print(f"🔥 An error occurred while loading data into '{table_name}': {e}")

print("\n🎉 Database setup is complete! You can now check your database tool to see the tables and data.")