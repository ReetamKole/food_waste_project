# create_sqlite_db.py
import pandas as pd
from sqlalchemy import create_engine
import os

# This will create a new file named food_waste.db
DB_FILE = "food_waste.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

csv_to_table_map = {
    'providers_data.csv': 'Providers',
    'receivers_data.csv': 'Receivers',
    'food_listings_data.csv': 'Food_Listings',
    'claims_data.csv': 'Claims'
}
data_folder = 'data'

for csv_file, table_name in csv_to_table_map.items():
    file_path = os.path.join(data_folder, csv_file)
    df = pd.read_csv(file_path)
    # Use table names without quotes for SQLite compatibility in pandas
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Created table '{table_name}' in {DB_FILE}")

print("SQLite database created successfully.")