# main.py
from fetch_data import fetch_data_from_postgres

def main():
    print("Fetching data from PostgreSQL...")
    json_outputs = fetch_data_from_postgres()
    
    if json_outputs:
        print("Data fetched successfully!")
        for table, json_data in json_outputs.items():
            print(f"\nTable: {table}")
            print(json_data[:100] + "...")  # Print a snippet of each table's data for verification
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()