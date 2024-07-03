To modify this script to run daily and only process new records, we'll need to implement a mechanism to track which records have been processed before. Here's an approach to achieve this:

1. Create a database or file to store the IDs of processed records.
2. When processing records, check against this database/file to determine if a record is new.
3. Only process and output new records.
4. Update the database/file with newly processed record IDs.

Let's modify the script to implement this functionality. We'll use a simple CSV file to store processed record IDs, but for a production environment, a proper database might be more suitable.



```python
import pandas as pd
import os
from datetime import datetime

def get_processed_ids(file_path):
    if os.path.exists(file_path):
        return set(pd.read_csv(file_path, header=None)[0])
    return set()

def save_processed_ids(file_path, ids):
    pd.DataFrame(list(ids)).to_csv(file_path, index=False, header=False)

def process_new_records():
    # File to store processed IDs
    processed_ids_file = "processed_ids.csv"
    processed_ids = get_processed_ids(processed_ids_file)

    # Read the lookup file into a DataFrame
    df_lookup = pd.read_csv("city_lookup.csv")

    # Read the customer data file into a DataFrame
    df_customers = pd.read_csv("customers-10000.csv")

    # Filter to only include rows where Country is 'United States' and Customer Id is new
    df_customers_filtered = df_customers[
        (df_customers["Country"] == "United States") & 
        (~df_customers["Customer Id"].isin(processed_ids))
    ]

    if df_customers_filtered.empty:
        print("No new records to process.")
        return

    # Merge the filtered customer DataFrame with the lookup DataFrame
    df_merged = df_customers_filtered.merge(
        df_lookup[["City", "UUID", "ZIP Code", "Area Code"]], on="City", how="left"
    )

    # Combine 'First Name' and 'Last Name' into 'Legal Name'
    df_merged["Legal Name"] = df_merged["First Name"] + " " + df_merged["Last Name"]

    # Add a new column 'Reviewed' with the static text "Reviewed by Bob"
    df_merged["Reviewed"] = "Reviewed by Bob"

    # Apply the column mapping
    column_mapping = {
        "Customer Id": "ID",
        "Email": "email address",
        "Legal Name": "Legal Name",
        "UUID": "UUID",
        "Reviewed": "Reviewed",
        "ZIP Code": "ZIP Code",
        "Area Code": "Area Code"
    }

    # Get current date for file naming
    current_date = datetime.now().strftime("%Y%m%d")

    # Iterate through unique cities and create a new file for each city
    for city in df_merged["City"].unique():
        df_city = df_merged[df_merged["City"] == city]
        df_city_mapped = df_city[list(column_mapping.keys())].rename(columns=column_mapping)
        
        # Define the file name based on the city and current date
        file_name = f"datavue_{city.replace(' ', '_').replace('/', '_')}_{current_date}.csv"
        
        # Write the DataFrame to a new CSV file
        df_city_mapped.to_csv(file_name, index=False)
        
        print(f"The new data for {city} has been written to '{file_name}'.")

    # Update processed IDs
    processed_ids.update(df_merged["Customer Id"])
    save_processed_ids(processed_ids_file, processed_ids)

    print(f"Processed {len(df_merged)} new records.")

if __name__ == "__main__":
    process_new_records()

```

Here's an explanation of the changes made to the script:

1. We've created two new functions: `get_processed_ids()` and `save_processed_ids()`. These functions read from and write to a CSV file that stores the IDs of processed records.

2. The main logic is now in a function called `process_new_records()`.

3. We filter the customer data to include only new records by checking against the set of processed IDs.

4. The output file names now include the current date, ensuring unique file names for each daily run.

5. After processing, we update the set of processed IDs and save it back to the CSV file.

To run this job daily, you can set up a cron job (on Unix-like systems) or a scheduled task (on Windows) that executes this script once a day. The script will only process and output new records each time it runs.

Here's how you might set up a cron job to run this script daily at midnight:

1. Open your crontab file:
   ```
   crontab -e
   ```

2. Add the following line:
   ```
   0 0 * * * /usr/bin/python3 /path/to/your/citydemp.py
   ```

Replace `/usr/bin/python3` with the path to your Python interpreter and `/path/to/your/citydemp.py` with the actual path to your script.

This setup will ensure that your script runs daily, processing only new records each time. The output files will be date-stamped, allowing you to track which records were processed on which day.
