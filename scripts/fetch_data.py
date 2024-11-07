# db_fetcher.py
import json
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine, text, inspect

def fetch_data_from_postgres(variables = "source"):
    
    '''
    This function fetches a grid of coordinates of a certain year provided in 
    the variables. If variables = "source" the function will look for the file in 
    '../data/fetch_param.json' to source the variables. Otherwise variables can be provided
    as dictionary. Variables must include [lat_min, lat_max, lon_min, lon_max, years]
    '''
    
    print("\n--- DB SIGN IN: ---")
    # Load configuration from .env file
    print("reading .env files...")
    config = dotenv_values()
    pg_user = config.get('POSTGRES_USER')
    pg_host = config.get('POSTGRES_HOST')
    pg_port = config.get('POSTGRES_PORT')
    pg_db = config.get('POSTGRES_DB')
    pg_pass = config.get('POSTGRES_PASS')
    pg_schema = config.get('POSTGRES_SCHEMA', 'public')

    # Create the database engine
    url = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(url, echo=False)
    inspector = inspect(engine)
    
    # Validate connection and list schemas
    schemas = inspector.get_schema_names()
    if schemas:
        print(f"successfully connected to:\t {pg_db}")
        print(f"available schemas:\t\t {', '.join(schemas)}")
    else:
        print('connection to database failed: aborting')
        return
    
    # Set default schema
    print(f'setting default schema to:\t {pg_schema}')
    with engine.begin() as conn:
        conn.execute(text(f'SET search_path TO {pg_schema};'))
    
    tables = inspector.get_table_names(schema=pg_schema)
    print(f'tables in default schema:\t {", ".join(tables)}')

    # Load fetch parameter
    if variables == "source":
        print("\n--- READING FETCHING PARAMETERS: ---")
        with open("../data/fetch_param.json", "r") as json_file:
            variables = json.load(json_file)

    for key, value in variables.items():
        print(f'{key}:\t {value}')
    
    # Filter tables based on year and parameters
    fetched_tables = ["elevation"]
    for t in tables:
        parts = t.split("_")
        year = parts[-1]
        if year.isdigit() and int(year) in variables["years"]:
            fetched_tables.append(t)
    
    print(f'>>> Fitting tables: {", ".join(fetched_tables)}')

    # Check columns for lat/lon requirements
    print("\n--- CHECKING TABLES: ---")
    table_columns = {}
    for t in fetched_tables:
        columns = inspector.get_columns(t, schema=pg_schema)
        table_columns[t] = [col["name"] for col in columns]

    for table, columns in table_columns.items():
        if not any(col in columns for col in ["lon", "longitude"]) or not any(col in columns for col in ["lat", "latitude"]):
            print(f"DISCARDED:\t{table} >>> does not feature 'lon/longitude' and 'lat/latitude' as columns")
            fetched_tables.remove(table)
        else:
            print(f"KEPT:\t\t{table}")

    # Fetch data for selected tables
    print("\n--- FETCHING DATA: ---")
    json_outputs = {}
    for ft in fetched_tables:
        columns = inspector.get_columns(ft, schema=pg_schema)
        column_names = [col["name"] for col in columns]
        
        if "lat" in column_names and "lon" in column_names:
            query = text(f"SELECT * FROM {pg_schema}.{ft} WHERE lat BETWEEN :lat_min AND :lat_max AND lon BETWEEN :lon_min AND :lon_max;")
        elif "latitude" in column_names and "longitude" in column_names:
            query = text(f"SELECT * FROM {pg_schema}.{ft} WHERE latitude BETWEEN :lat_min AND :lat_max AND longitude BETWEEN :lon_min AND :lon_max;")
        else:
            print(f'{ft} does not have required lat/lon or latitude/longitude columns')
            continue
        
        df = pd.read_sql(query, con=engine, params={
            'lat_min': variables['lat_min'],
            'lat_max': variables['lat_max'],
            'lon_min': variables['lon_min'],
            'lon_max': variables['lon_max']
        })
        json_outputs[ft] = df.to_json(orient='records')
        print(f'>>> SUCCESS: {ft} data fetched')

    return json_outputs
