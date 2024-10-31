## IMPORTS
import re
import ast
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, text, inspect
from dotenv import dotenv_values
from meteostat import Stations, Monthly

## FUNCTIONS
# >>> Generalized user input to set script variables
def prompt_user():
    while True:
        user_input = input(">> Please provide input (y/n): ").strip().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

##DEBUGGING
print("\nDo you want to run the script in debug mode? (Skips db connection and sets all other user inputs states to 'def')")
debug_state = prompt_user()
            
# >>> Adjust sourcing timestamps to only allow for full years
def adjust_dates_for_full_years(start, end):
    # Check for NaN values and handle them
    if pd.isna(start) or pd.isna(end): 
        return None, None
    # Convert to datetime if not already
    start = pd.to_datetime(start) 
    end = pd.to_datetime(end) 
    # Adjust start to the next January 1st if not already on that date
    if start.month != 1 or start.day != 1:
        start = datetime(start.year + 1, 1, 1)
    # Adjust end to the previous December 31st if not already on that date
    if end.month != 12 or end.day != 31:
        end = datetime(end.year-1, 12, 31)
    # Ensure start is before or the same as end
    if start > end:
        return None, None
    # return adjusted start and end
    return start, end         

#define conditional aggreagations to only take years into account that lack one months but not more
def conditional_aggregate_sum(x):
    if x.dropna().count() >= 11:  # Count only non-NaN values
        return x.sum()  # Or use another aggregation, like mean, etc.
    else:
        return float('nan')  # Return NaN if less than 11 non-NaN records

def conditional_aggregate_mean(x):
    if x.dropna().count() >= 11:  # Count only non-NaN values
        return x.mean() 
    else:
        return float('nan')  # Return NaN if less than 11 non-NaN records
    
def conditional_aggregate_min(x):
    if x.dropna().count() >= 11:  # Count only non-NaN values
        return x.min() 
    else:
        return float('nan')  # Return NaN if less than 11 non-NaN records
    
def conditional_aggregate_max(x):
    if x.dropna().count() >= 11:  # Count only non-NaN values
        return x.max() 
    else:
        return float('nan')  # Return NaN if less than 11 non-NaN records

#define conditional aggreagations to only take years into account that lack one months but not more
def conditional_aggregate_sd(x):
    if x.dropna().count() >= 11:  # Count only non-NaN values
        return np.std(x.dropna())  
    else:
        return float('nan')  # Return NaN if less than 11 non-NaN records   

## START SCRIPT

if not debug_state:
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
        
    # check database tables
    print(f'tables in default schema: \t {", ".join(inspector.get_table_names(schema=pg_schema))}:')


## CHECK WHETHER 'meteostat_stations' IN DATABASE IS UP TO DATE
print("\n--- CHECKING STATIONS DATA: --- ")
# if not ask for user input to source stations from the python library de-novo

# Retrieve all Meteostat weather stations
stations = Stations()
# Fetch the list of all stations
# Convert the result to a DataFrame
df_stations = stations.fetch()
df_stations = df_stations.copy().reset_index()

if not debug_state:
    if df_stations.shape != pd.read_sql(sql=text('SELECT * FROM meteostat_stations;'), con=engine).shape:
        print("'meteostat_stations' appears outdated do you want to update?")
        #ask for user input
        upload_stations = prompt_user()
    elif df_stations.shape != pd.read_sql(sql=text('SELECT * FROM meteostat_stations;'), con=engine).shape:
        print("'meteostat_stations' is up to date")
        upload_stations = False

## DEFINE RETRIEVAL TIME FRAME
print("\n--- SETTING RETRIEVAL PARAMETERS: --- ")
def get_custom_dates():
    date_pattern = r"^\d{2}-\d{2}-\d{4},\d{2}-\d{2}-\d{4}$"
    while True:
        user_input = input(">> 'START, END' dates as 'DD-MM-YYYY,DD-MM-YYYY': \n>> input 'def' to default to 5 years ago (accounting for meteostat buffering time): ")
        #default to current year if applicable
        if user_input == 'def':
            start = pd.to_datetime("01-01-"+str(datetime.today().year-5), dayfirst = True)
            end = pd.to_datetime("31-12-"+str(datetime.today().year-5), dayfirst = True)
            print(f'defautling to: START = {start}, END = {end}')
            #to exit 
            return start,end
        elif bool(re.match(date_pattern, user_input)):
            start = pd.to_datetime(str.split(user_input, ",")[0], dayfirst = True)
            end = pd.to_datetime(str.split(user_input, ",")[1], dayfirst = True)
            #check if start is before end:
            if end < start:
                print("Warning: please provide the dates as from START to END")
                continue
            print(f"valid date format: START = {start}, END = {end}") 
            #to exit
            return start,end
        else:
            print("Invalid input. Please enter daterange or 'def'.")

if debug_state:
    start = pd.to_datetime("01-01-"+str(datetime.today().year-6), dayfirst = True)
    end = pd.to_datetime("31-12-"+str(datetime.today().year-5), dayfirst = True) 
else: 
    start, end = get_custom_dates()

## SUBSET STATIONS 
#get the custom filter
def get_custom_filter():
    excluded_columns = {'hourly_start', 'hourly_end', 'daily_start', 'daily_end', 'monthly_start', 'monthly_end'}
    filtered_columns = [col for col in df_stations.columns if col not in excluded_columns]
    
    while True:
        user_input = input(f"\n>> Please enter a filter for meteostat stations (as dictionary):\n>> possible keys are: {', '.join(filtered_columns)}\n>> input 'def' to fetch the whole dataset: ")
        # Default to full dataset if applicable
        if user_input == 'def':
            custom_filter = {}
            print(f"Defaulting to full dataset: currently {df_stations.shape[0]} meteorological stations")
            return custom_filter
        # Attempt to parse the user input as a dictionary
        try:
            user_input = ast.literal_eval(user_input)
            if isinstance(user_input, dict):
                # Check if all keys in user input are in filtered columns
                if all(key in filtered_columns for key in user_input.keys()):
                    custom_filter = user_input
                    print(f"Valid filter provided for keys: {', '.join(custom_filter.keys())}")
                    return custom_filter
                else:
                    print("Warning: Please only filter for provided columns")
            else:
                print("Invalid input. Please enter a dictionary or 'def'.")
        except (ValueError, SyntaxError):
            print("Invalid input format. Please enter a valid dictionary or 'def'.")
# Call the function

if debug_state:
    custom_filter = {}
else:
    custom_filter = get_custom_filter()

#apply the fillter to df_stations
if custom_filter != {}:
    for key, value in custom_filter.items():
        df_stations = df_stations[df_stations[key] == value]

## EXTRACT stations dataframe for timeframe 
print("")
# Loop through individual stations
total_rows = len(df_stations)
bar_length = 30
df_meta = pd.DataFrame()

# Assume start and end are defined elsewhere or add them as arguments
for i, row in df_stations.iterrows():
    # Calculate progress percentage
    percent_complete = (i + 1) / total_rows
    filled_length = int(bar_length * percent_complete)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    # Initialize/reset error message
    Error = ""

    # Extract station information
    station_id = row["id"]
    name = row["name"]
    country = row["country"]

    # Get station parameters
    start_i = row["monthly_start"]
    end_i = row["monthly_end"]

    # Adjust the dates to only take full years into account
    start_i_adj, end_i_adj = adjust_dates_for_full_years(start_i, end_i)

    # Validate the adjusted dates
    if start_i_adj is None or end_i_adj is None:
        Error = f"Error1: No date range detected for {station_id}. Skipping..."
    elif start_i_adj > end_i_adj:
        Error = f"Error2: Invalid date range for station {station_id}. Skipping..."
    else:
        # Check and adjust start and end times based on provided bounds
        if start >= start_i_adj:
            start_i_adj = start
        if end <= end_i_adj:
            end_i_adj = end

        # If dates are valid, create a DataFrame for the station metadata
        df_i = pd.DataFrame({
            "id": [station_id],
            "name": [name],
            "country": [country],
            "start": [start_i_adj],
            "end": [end_i_adj]
        })
        # Concatenate the station metadata to the main DataFrame
        df_meta = pd.concat([df_meta, df_i], ignore_index=True)

    # Display the progress bar and current station info
    print(f"Progress: |{bar}| {percent_complete * 100:.2f}% \t Checking dates for: {station_id} | {name[:10]}... \t | {country} | {Error}", end="\r")

    # Only run the first 20 iterations for debugging
    if debug_state and i > 20:
        break
        
print("")
print(f"\nIn total: {df_meta.shape[0]} stations are within range ({start.strftime("%d-%m-%Y")} to {end.strftime("%d-%m-%Y")})")

#Fetching data
print("\n--- FETCHING DATA: ---\n")

df_agg = pd.DataFrame()
total_rows = len(df_meta)
bar_length = 30
#iterrate through dataframe
for i, row in df_meta.iterrows():
    station_id = row["id"]
    name = row["name"]
    country = row["country"]
    
    # Calculate and print progress percentage
    percent_complete = (i + 1) / total_rows
    filled_length = int(bar_length * percent_complete)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    # Display the progress bar and the current station info
    print(f"Progress: |{bar}| {percent_complete * 100:.2f}% \t\t Extracting data for: {station_id} | {name} | {country} |                           ", end="\r")
    
    #fetch data for respective station with the previously defined start and end date
    df_i = Monthly(row["id"], #station 
                start = pd.to_datetime(row["start"]), #start
                end= pd.to_datetime(row["end"]) #end
                )
    df_i = df_i.fetch().reset_index()
    #aggregate the data for each year
    df_yearly = df_i.groupby(df_i['time'].dt.year).agg({
    'tavg': conditional_aggregate_mean, 
    'tmin': conditional_aggregate_min,
    'tmax': conditional_aggregate_max,
    'prcp': conditional_aggregate_sum,
    'wspd': conditional_aggregate_mean,
    'pres': conditional_aggregate_mean,
    'tsun': conditional_aggregate_sum
    })
    df_yearly = df_yearly.reset_index()
    df_yearly["id"] = station_id
    # Concatenate the station metadata to the main DataFrame
    df_agg = pd.concat([df_agg, df_yearly], ignore_index=True)
    
    if debug_state and i>20:
        break

print("")

potential_stations = df_meta.shape[0]*(end.year-start.year+1)
extracted_stations = df_agg.shape[0]

print(f"\nFetch and aggregation successful for: {extracted_stations} data points ({round(100*extracted_stations/potential_stations,2)}% of {df_meta.shape[0]} stations over {(end.year-start.year+1)} years)") 
#Fetching data
print("\n--- UPLOADING TO DATABASE: ---\n")

for time in df_agg["time"].unique():
    df_sub = df_agg[df_agg["time"] == time]
    name = f'meteostat_{time}'
    print(f"pushing '{name}' to sql")
    if not debug_state and custom_filter == {}:
        df_sub.to_sql(name, engine, if_exists='replace', index=False)
    if not debug_state and custom_filter != {}:
        df_sub.to_sql(f'{name}_filtered', engine, if_exists='replace', index=False)


## PRINT END OF SCRIPT STATEMENT
print("\n--- END ---")

