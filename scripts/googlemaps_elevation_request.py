
## IMPORTS
import requests
import json
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dotenv import dotenv_values
from sqlalchemy import create_engine, text, inspect

#SIGN IN TO PostgreSQL
print ("\n--- DB SIGN IN: ---")
#load values from the .env file
print("reading .env files...")
config = dotenv_values()
# define variables for the login
pg_user = config['POSTGRES_USER']
pg_host = config['POSTGRES_HOST']
pg_port = config['POSTGRES_PORT']
pg_db = config['POSTGRES_DB']
pg_pass = config['POSTGRES_PASS']
pg_schema = config['POSTGRES_SCHEMA']
# Now building the URL with the values from the .env file
url = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
#create engine 
engine = create_engine(url, echo=False)    
# check if the connection is successfully established or not
inspector = inspect(engine)
schemas = inspector.get_schema_names()
if schemas != []:
    print(f"succesfully connected to: \t {pg_db}")
    print(f"available schemas: \t\t {", ".join(schemas)}")
else:
    print(f'connection to database failed: aborting')
# set default schema defined in .env
if 'pg_schema' in locals():
    print(f'setting default schema to: \t {pg_schema}')
    with engine.begin() as conn: 
        result = conn.execute(text(f'SET search_path TO {pg_schema};'))  #possible to cascade with ,public; then it will search in my_schema first and then in public
else:
    print(f'no default schema set: \t defaulting to public')
    pg_schema = "public"
    with engine.begin() as conn: 
        result = conn.execute(text(f'SET search_path TO public;'))  #possible to cascade with ,public; then it will search in my_schema first and then in public

tables = inspector.get_table_names(schema=pg_schema)
print(f'tables in default schema: \t {", ".join(tables)}:')
  
#FETCH CORDINATES
print ("\n--- FETCHING Coordinate grid: ---")


#checkout one of the earthdata tables
earthdata_table = ""
for t in tables:
    if "earthdata" in t:
        earthdata_table = t
    if earthdata_table != "":
        break

print(f"fetching from '{earthdata_table}'")
#and read latitude and longitude it into a pd dataframe
earthdata_table = pd.read_sql(sql=text(f'SELECT lon,lat FROM {earthdata_table};'), con=engine)
print(f'retrieved {earthdata_table.shape[0]} pixels')

# parse data into API compatible format
data = {
    "locations": [{"latitude": row['lat'], "longitude": row['lon']} for index, row in earthdata_table.iterrows()]
}


print("\n--- REQUESTING DATA FROM OPEN-ELEVATION: ---")
# Define the API endpoint and headers
url = "https://api.open-elevation.com/api/v1/lookup"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Function to make a POST request to the API with retries
def make_request(batch, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps({"locations": batch}))
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:  # Wait and retry if not the last attempt
                time.sleep(delay)
            else:
                return None

# Setup for progress bar
total_rows = len(data["locations"])
total_rows = 200 #DEBUGGING
bar_length = 30
batch_size = 50  # Adjust based on API limitations
sleep_time = 0.5  # Adjust dependent on API limitations
locations = data["locations"]
results = []

print(f"API url: \t\t\t{url}")
print(f"request batch size: \t\t{batch_size}")
print(f"sleep time between requests: \t{sleep_time}")
print("")

# Loop through batches with progress bar
for i in range(0, total_rows, batch_size):
    batch = locations[i:i + batch_size]
    result = make_request(batch)

    if result is not None and 'results' in result:
        results.extend(result['results'])
    else:
        print(f"Batch {i // batch_size + 1} failed, skipping...")

    # Update and display progress bar
    percent_complete = (i + batch_size) / total_rows
    bar = '#' * int(bar_length * percent_complete) + '-' * (bar_length - int(bar_length * percent_complete))
    print(f"Progress: |{bar}| {percent_complete * 100:.2f}%", end="\r")

    # Optional: Add a delay to avoid rate-limiting
    time.sleep(sleep_time)

print("\nCompleted!")


print("\n--- UPLOADING TO DATABASE: ---\n")

pd.DataFrame(results).to_sql("elevation", if_exists='replace', index=False, con=engine)
#engine.dispose()

print("Upload successfull")

## PRINT END OF SCRIPT STATEMENT
print("\n--- END ---")

