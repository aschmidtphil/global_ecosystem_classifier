import os
import pandas as pd
import xarray as xr
from sqlalchemy import create_engine
from dotenv import load_dotenv
import earthaccess


# Login to EarthData
auth = earthaccess.login()

# Dataset parameters
doi_code = "10.5067/9SQ1B3ZXP2C5"  # GLDAS 2.1
short_name = "GLDAS_NOAH025_M"
bounding_box = (-180, -90, 180, 90)

# Define the range for GLDAS 2.1 (2000-2024)
start_year = 1948
end_year = 1999

# Load environment variables
load_dotenv()
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_SCHEMA = os.getenv('POSTGRES_SCHEMA')  # Load the schema from .env

# Create the database connection string and engine
connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(connection_string)

# Function to clean column names
def clean_column_names(columns):
    new_columns = []
    for col in columns:
        col = col.replace('tavg', '').replace('_f_', '').replace('inst', '')

        if col.startswith('SoilMoi0_10cm'):
            col = col.replace('SoilMoi0_10cm', 'SoilM010')
        elif col.startswith('SoilMoi10_40cm'):
            col = col.replace('SoilMoi10_40cm', 'SoilM1040')
        elif col.startswith('SoilMoi40_100cm'):
            col = col.replace('SoilMoi40_100cm', 'SoilM40100')
        elif col.startswith('SoilMoi100_200cm'):
            col = col.replace('SoilMoi100_200cm', 'SoilM100200')
        elif col.startswith('SoilTMP0_10cm'):
            col = col.replace('SoilTMP0_10cm', 'SoilT010')
        elif col.startswith('SoilTMP10_40cm'):
            col = col.replace('SoilTMP10_40cm', 'SoilT1040')
        elif col.startswith('SoilTMP40_100cm'):
            col = col.replace('SoilTMP40_100cm', 'SoilT40100')
        elif col.startswith('SoilTMP100_200cm'):
            col = col.replace('SoilTMP100_200cm', 'SoilT100200')
        
        new_columns.append(col)
    
    return new_columns

# Process data for each year
for year in range(start_year, end_year + 1):
    print(f"Processing data for year: {year}")

    # Date range for the year
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    earthdata_df = pd.DataFrame()

    try:
        # Search for data
        results = earthaccess.search_data(
            doi=doi_code,
            temporal=(start_date, end_date),
            bounding_box=bounding_box,
            short_name=short_name
        )
        
        fs = earthaccess.open(results)  # Open file URLs
        ds = xr.open_mfdataset(fs, chunks=None)

        for var_name, variable_data in ds.data_vars.items():
            print(f"Processing variable: {var_name}")

            if 'lon' not in variable_data.dims or 'lat' not in variable_data.dims:
                print(f"Skipping {var_name} as it lacks 'lon' and 'lat' dimensions.")
                continue
            
            var_df = variable_data.to_dataframe().dropna(subset=[var_name]).reset_index()

            aggregated_df = var_df.groupby(['lon', 'lat']).agg(
                min_value=(var_name, 'min'),
                max_value=(var_name, 'max'),
                avg_value=(var_name, 'mean')
            ).reset_index()

            aggregated_df.rename(columns={
                'min_value': f'{var_name}_min',
                'max_value': f'{var_name}_max',
                'avg_value': f'{var_name}_avg'
            }, inplace=True)
            
            earthdata_df = aggregated_df if earthdata_df.empty else pd.merge(earthdata_df, aggregated_df, on=['lon', 'lat'], how='outer')

        # Clean and save data
        earthdata_df.columns = clean_column_names(earthdata_df.columns)
        earthdata_df.columns = [col.replace('__', '_') for col in earthdata_df.columns]
        
        # Save to CSV
        csv_filename = f"earthdata_{year}.csv"
        earthdata_df.to_csv(csv_filename, index=False)
        print(f"Yearly data for {year} saved to {csv_filename}")

        # Define table name and upload to SQL database
        table_name = f"earthdata_{year}"
        earthdata_df.to_sql(table_name, engine, if_exists='replace', index=False, schema=POSTGRES_SCHEMA)
        print(f"Data for {year} uploaded to table {table_name} successfully.")

    except Exception as e:
        print(f"An error occurred while processing data for year {year}: {e}")

print("Data processing and upload complete for all specified years.")
