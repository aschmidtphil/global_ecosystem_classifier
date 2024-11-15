import argparse
import json
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine, text, inspect
import numpy as np
from sklearn.linear_model import LinearRegression

# ARGUMENTPARSER SETUP
parser = argparse.ArgumentParser(
    description="Script for ecosystem predictions with debugging and customization options"
)
parser.add_argument('--silent', action='store_true', help="Suppress print statements.")
parser.add_argument('--debug', action='store_true', help="Enable debugging mode.")
parser.add_argument('--iterations_j', type=int, default=2, help="Number of iterations for debugging outer loop (Parameters). Default: 2")
parser.add_argument('--iterations_i', type=int, default=1000, help="Number of iterations for debugging inner loop (Pixels). Default: 1000")
parser.add_argument('--save_r_squared', action='store_true', help="Save R-squared values to a local JSON file. Default: False")
parser.add_argument('--schema_in', type=str, default="ecosystem_outputs", help="Input schema name. Default: 'ecosystem_outputs'")
parser.add_argument('--schema_out', type=str, default="ecosystem_predictions", help="Output schema name. Default: 'ecosystem_predictions'")
parser.add_argument(
    '--predict_year', 
    type=int, 
    required=True, 
    help="Year to predict. This argument is required and must be specified."
)

args = parser.parse_args()

# Use argparse values for configuration
silent = args.silent
debugging = args.debug
iterations_j = args.iterations_j
iterations_i = args.iterations_i
save_r_squared = args.save_r_squared

# Existing variables derived from argparse
schema_in = args.schema_in
schema_out = args.schema_out
predict_year = args.predict_year

df_output = pd.DataFrame()
r_squared_dict = {}

# --- DB SIGN-IN ---

if not silent: print("\n--- DB SIGN IN: ---\nreading .env files...")
config = dotenv_values()
pg_user = config.get('POSTGRES_USER')
pg_host = config.get('POSTGRES_HOST')
pg_port = config.get('POSTGRES_PORT')
pg_db = config.get('POSTGRES_DB')
pg_pass = config.get('POSTGRES_PASS')
if schema_in == "env":
    pg_schema = config.get('POSTGRES_SCHEMA', 'public')
else:
    pg_schema = schema_in
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
if not silent: print(f'>> "Output" tables in "{pg_schema}": [{len(output_tables)}] {", ".join(output_tables)[:40]} ...')

# --- DEFINE COLUMN NAMES --- #

column_names = []

for t in output_tables:
    # Write query to fetch column names
    query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = '{pg_schema}' AND table_name = '{t}';
    """
    # Fetch column names as a DataFrame
    df_columns = pd.read_sql(query, con=engine)
    # Extend the list with column names
    column_names.extend(df_columns['column_name'].tolist())

# Remove duplicates and sort for clarity
#drop ["lat","lon","predicted_ecosystem"] from the column names as as we don't want to loop through them
column_names = sorted(set(column_names) - set(["lat","lon","predicted_ecosystem"]))

# --- LOOP THROUGH COLUMNS --- #

if not silent: print("\n--- FETCHING DATA: ---\n")
j = -1

for column_j in column_names:
    
    #break for debugging:
    if debugging == True and column_j == column_names[iterations_j]:
        break
    
    #define progress bar_1
    bar_length_1 = 25
    #calculate progress and depict
    j = j+1
    percent_complete_1 = (j + 1) / len(column_names)
    filled_length_1 = int(bar_length_1 * percent_complete_1)
    bar_1 = '█' * filled_length_1 + '-' * (bar_length_1 - filled_length_1)
    
    # Initialize an empty DataFrame to store combined pixel values
    df_j = pd.DataFrame()

    for table_k in output_tables:
        # Retrieve column_j along with lat and lon for the current table
        query = text(f'SELECT lat, lon, "{column_j}" FROM {pg_schema}.{table_k};')
        
        # Extract the year from the table name
        year = None
        for part in table_k.split("_"):
            if part.isdigit():
                year = int(part)
        
        print(f"Processing:\t{column_j} from year {year}", end="\r", flush=True)
        
        # Fetch the data
        df_k = pd.read_sql(query, con=engine)
        
        # Rename the value column to the corresponding year
        df_k = df_k.rename(columns={column_j: year})
        
        # Merge df_k into the main dataframe df_j
        if df_j.empty:
            df_j = df_k  # Initialize with the first dataframe
        else:
            df_j = pd.merge(df_j, df_k, on=["lat", "lon"], how="outer")  # Full outer join

    #get pixel_n
    pixel_n=df_j.shape[0]

    if not silent: print(f"\n\t\tfetching complete: {pixel_n} pixels found")

    # Drop rows where all columns except 'lat' and 'lon' are NaN
    df_j = df_j.dropna(subset=df_j.columns.difference(["lat", "lon"]), how="all")
    if pixel_n == df_j.shape[0]:
        if not silent: print("\t\tall pixels contained at least 1 value\n")
    else:
        if not silent: print(f"\t\t[{pixel_n-df_j.shape[0]}] pixels dropped: no-values\n")
    
# --- CALCULATE PREDICTION FOR COLUMN --- #

    # initialize/reset variables
    pixels_data = []
    df_predict = pd.DataFrame(columns=["lat", "lon", column_j, "r_squared"])
    total_rows = df_j.shape[0]
    bar_length_2 = 25

    # Loop through each row of df_j using enumerate for iteration control
    for i, (index, row) in enumerate(df_j.iterrows()):
        # Extract data for the current pixel, excluding 'lat' and 'lon'
        lat_i = row["lat"]
        lon_i = row["lon"]
        df_pixel = row.drop(["lat", "lon"])
        df_pixel = {"year": list(df_pixel.index), column_j: list(df_pixel.values)}
        df_pixel = pd.DataFrame(df_pixel)
        
        # Prepare data for the model
        X, y = np.array(df_pixel["year"]).reshape(-1, 1), np.array(df_pixel[column_j])

        # Initialize model
        model = LinearRegression()
            
        # Check if there is enough data to fit the model
        if len(X) > 1:
            # Fit the model and calculate R-squared
            model.fit(X, y)
            r_squared = model.score(X, y)
            predict_val = model.predict(np.array([[predict_year]]))[0]  # Extract single value
        else:
            # Handle cases with insufficient data
            r_squared = np.nan
            predict_val = np.nan  # Single NaN value for the year

        # Create a new DataFrame with the row to append
        new_row = pd.DataFrame({
            "lat": lat_i,
            "lon": lon_i,
            column_j: [predict_val],
            "r_squared": [r_squared],
        })

        # Explicitly set the dtypes to match df_predict to avoid warnings
        new_row = new_row.astype(df_predict.dtypes.to_dict())

        # Append the new row to the results DataFrame
        df_predict = pd.concat([df_predict, new_row], ignore_index=True)    
        
        #calculate progress and depict
        percent_complete_2 = (i + 1) / total_rows
        filled_length_2 = int(bar_length_2 * percent_complete_2)
        bar_2 = '█' * filled_length_2 + '-' * (bar_length_2 - filled_length_2)
        
        print(f"Progress: |{bar_2}| {percent_complete_2 * 100:.2f}% for {column_j} of |{bar_1}| {percent_complete_1 * 100:.2f}% [predict {predict_year}]", end="\r", flush=True)

        # Break the loop after 100 iterations
        if debugging == True and i >= iterations_i:
            break
        
    #calculate average R-squared and drop column
    r_squared_mean = df_predict["r_squared"].mean()
    df_predict = df_predict.drop("r_squared", axis=1)

    #save to df_column_j
    df_column_j = df_predict
    #and r squared to dictionary
    r_squared_dict[column_j] = r_squared_mean
    
    # Merge df_k into the main dataframe df_j
    if df_output.empty:
        df_output = df_column_j  # Initialize with the first dataframe
    else:
        df_output = pd.merge(df_output, df_column_j, on=["lat", "lon"], how="outer")  # Full outer join
    if not silent: print("\n\n\n")
    

# --- SAVE OUTPUT DATA TO SQL--- #

if not silent: print("\n--- UPLOADING TO DATABASE: ---\n")

#handling output 
name = "prediction_"+str(predict_year)
df_output.to_sql(name, engine, if_exists='replace', index=False, schema=schema_out)
if not silent: print(f"pushing '{name}' to sql")

#handling r_squared
if save_r_squared:
    # Save the dictionary as a JSON file
    file_name="r_squared_"+str(predict_year)+".json"
    with open(file_name, "w") as json_file:
        json.dump(r_squared_dict, json_file, indent=4)
    if not silent: print(f"saving '{file_name}' to local directory")

## PRINT END OF SCRIPT STATEMENT
if not silent: print("\n--- END ---")