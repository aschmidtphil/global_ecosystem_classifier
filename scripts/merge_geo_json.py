import json
import pandas as pd

def merge_geo_json(json_outputs, silent=True):
    # Initialize an empty list to store the DataFrames
    dfs = []
    # Loop over each table in json_outputs
    for key, data in json_outputs.items():
        # Parse JSON string if necessary
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError as e:
                if not silent: print(f"Error decoding JSON for table '{key}': {e}")
                continue  # Skip this table if JSON parsing fails
        else:
            parsed_data = data

        # Convert parsed data to a DataFrame
        try:
            df = pd.DataFrame(parsed_data)
        except ValueError as e:
            if not silent: print(f"Error creating DataFrame for table '{key}': {e}")
            continue  # Skip this table if DataFrame creation fails

        # Standardize column names to 'lat' and 'lon' for merging
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        elif 'lat' not in df.columns or 'lon' not in df.columns:
            if not silent: print(f">>> Warning: Table '{key}' is missing required 'lat'/'lon' or 'latitude'/'longitude' columns.")
            continue  # Skip tables without valid latitude/longitude columns

        # Append the DataFrame to the list
        dfs.append(df)

    # Merge all DataFrames on 'lat' and 'lon' if there are valid DataFrames
    if dfs:
        merged_df = dfs[0]
        for df in dfs[1:]:
            try:
                merged_df = merged_df.merge(df, on=['lat', 'lon'], how='outer')
            except KeyError as e:
                if not silent: print(f"Error merging table due to missing 'lat'/'lon' columns: {e}")
                continue  # Skip merging if 'lat'/'lon' columns are missing

        # Display the merged DataFrame
        if not silent: print("\nMerged DataFrame:")
        if not silent: print(merged_df.head(5))
    else:
        if not silent: print("No valid tables with latitude and longitude data were found.")
    return merged_df if dfs else pd.DataFrame()