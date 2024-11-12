
# IMPORTS
import json
import pandas as pd
import sys

from fetch_data import fetch_data_from_postgres
from merge_geo_json import merge_geo_json

from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import dotenv_values

#default to expand training data for grid resolution if not given
grid_resolution = 0.25
#take argument one if given
if len(sys.argv) > 1:
    grid_resolution = float(sys.argv[1])

#LOAD TRAINING LOCATIONS
print("\n--- LOAD TRAINING LOCATIONS: ---")
with open("../data/ecosystem_locations.json", "r") as json_file:
            training_data = json.load(json_file)
            
# confirm training data
print(f'found {len(training_data.keys())} keys for training data points')
print(f'keys: {", ".join(list(training_data.keys()))[:25]},...')

# ASSIGN TRAINING DATA
print("\n--- ASSIGN TRAINING DATA: ---")

print(f"\n Training data bounding boxes are expanded according to grid resolution: {grid_resolution}")

#empty dataframe for merged training data
meta_df = pd.DataFrame()

total_rows = len(training_data.keys())
bar_length = 50
i = -1

# loop through items training data
for key in training_data.keys():
    i = i+1
    data_key = training_data[key]
    ecosystem_key = data_key["ecosystem"]
    variables_key = data_key["variables"]
    # Adjust lat/lon with grid resolution to ensure at least one pixel is fetched
    lat_min = max(-90, variables_key['lat_min'] - grid_resolution / 2)
    lat_max = min(90, variables_key['lat_max'] + grid_resolution / 2)
    lon_min = max(-180, variables_key['lon_min'] - grid_resolution / 2)
    lon_max = min(180, variables_key['lon_max'] + grid_resolution / 2)
    
    #sanity checks:
    print(f'\n\t\t{key.upper()}')
    print(f'Ecosystem:\t{ecosystem_key}')
    print(f'Variables:\t{", ".join(f"{k}: {v}" for k, v in variables_key.items())}')
    print(f'Grid expand to:\tlat_min: {lat_min}, lat_max: {lat_max}, lon_min: {lon_min}, lon_max: {lon_max}, grid resolution: {grid_resolution}')   
    
    #fetch data
    json_outputs = fetch_data_from_postgres(variables=variables_key, silent = True, grid_resolution=grid_resolution)
    # Initialize an empty list to store the temporary dataframes
    merged_data_key = merge_geo_json(json_outputs, silent=True)
    print(f'Pixels added:\t{merged_data_key.shape[0]}')
    merged_data_key["ecosystem"] = ecosystem_key
    merged_data_key["name"] = key
    meta_df = pd.concat([meta_df, merged_data_key], ignore_index=True)
    print(f'Pixels TOTAL:\t{meta_df.shape[0]}')
    
    #calculate progress and depict
    percent_complete = (i + 1) / total_rows
    filled_length = int(bar_length * percent_complete)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"\nProgress: |{bar}| {percent_complete * 100:.2f}%")

#SIGN IN TO PostgreSQL
print ("\n--- DB SIGN IN: ---")
#load values from the .env file
print("")
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
    print(f"available schemas: \t\t {', '.join(schemas)}")
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

#UPLOAD TRAINING DATA
print ("\n--- UPLOAD TRAINING DATA TO SQL: ---")

filename = datetime.now().strftime('%Y%m%d')+'_trainingdata'
meta_df.to_sql(filename, engine, if_exists='replace', index=False)
print(f"\n training data uploaded to '{pg_db}' as '{filename}'")

print ("\n--- END ---")