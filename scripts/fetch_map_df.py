import json
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine, text, inspect

def fetch_map_df(year=2020, region="World", plotting_parameters=["predicted_ecosystem"], silent=False, schema = "ecosystem_outputs"):
    
    '''
    Fetches geospatial data from a PostgreSQL database for a specified year and region, filtered by latitude and longitude bounds.

    This function connects to a PostgreSQL database using credentials from a `.env` file, sets the database schema, identifies relevant tables containing "output" in the name, and selects a specific table based on the given `year`. It fetches data within the bounding box of the specified `region`, selecting columns defined in `plotting_parameters`. The resulting DataFrame is returned and optionally displays connection details and processing steps.

    Parameters:
    - year (int): The year to filter tables by.
    - region (str): The geographic region, which corresponds to bounding box settings in `bounding_boxes.json`.
    - plotting_parameters (list): List of columns to fetch; includes `lat` and `lon` if not specified.
    - silent (bool): If True, suppresses print statements for a quieter output.
    - schema (str): The database schema to use; defaults to "ecosystem_outputs" or can read from `.env` if set to "env".

    Returns:
    - pd.DataFrame: DataFrame containing the fetched geospatial data.
    '''
    
    # Load configuration from .env file
    if not silent: print("\n--- DB SIGN IN: ---\nreading .env files...")
    config = dotenv_values()
    pg_user = config.get('POSTGRES_USER')
    pg_host = config.get('POSTGRES_HOST')
    pg_port = config.get('POSTGRES_PORT')
    pg_db = config.get('POSTGRES_DB')
    pg_pass = config.get('POSTGRES_PASS')
    if schema == "env":
        pg_schema = config.get('POSTGRES_SCHEMA', 'public')
    else:
        pg_schema = schema

    # Create the database engine
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}', echo=False)
    inspector = inspect(engine)

    # Validate connection
    if inspector.get_schema_names():
        if not silent: print(f">> Connected to: {pg_db}\n>> Schemas available: {', '.join(inspector.get_schema_names())}")

    # Set schema
    with engine.begin() as conn:
        conn.execute(text(f'SET search_path TO {pg_schema};'))

    # Identify output tables
    output_tables = [t for t in inspector.get_table_names(schema=pg_schema) if "output" in t.split("_")]
    if not silent: print(f'>> "Output" tables in "{pg_schema}": [{len(output_tables)}]{", ".join(output_tables)[:40]} ...')

    # Load bounding box data
    with open("../scripts/bounding_boxes.json", "r") as json_file:
        bounding_boxes = json.load(json_file)

    # Select the relevant table based on year
    table_region = next((t for t in output_tables if str(year) in t.split("_")), None)
    if table_region is None:
        raise ValueError("No matching table found for the specified year.")

    # Prepare columns to select
    if "lat" not in plotting_parameters and "lon" not in plotting_parameters:
        plotting_parameters.extend(["lat", "lon"])
    # Prepare columns to select with quotes for case sensitivity
    param_str = ", ".join([f'"{param}"' for param in plotting_parameters])

    
    if not silent: print(f'\nFetching region "{region}" and parameters "{param_str}" from "{table_region}"')

    # Define and execute query
    query = text(f"SELECT {param_str} FROM {pg_schema}.{table_region} WHERE lat BETWEEN :lat_min AND :lat_max AND lon BETWEEN :lon_min AND :lon_max;")
    df = pd.read_sql(query, con=engine, params={
        'lat_min': bounding_boxes[region]["variables"]["lat_min"],
        'lat_max': bounding_boxes[region]["variables"]["lat_max"],
        'lon_min': bounding_boxes[region]["variables"]["lon_min"],
        'lon_max': bounding_boxes[region]["variables"]["lon_max"]
    })

    if not silent: print(f'\nSUCCESS: fetched {df.shape[0]} records for "{", ".join(df.columns)}"')
    return df
