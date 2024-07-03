Certainly, I can modify the script to remove processed IDs that no longer appear in the data file. This is a good practice to keep the processed IDs list current and prevent it from growing indefinitely. Let's update the script to include this functionality.



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

    # Get all current customer IDs
    current_ids = set(df_customers["Customer Id"])

    # Remove processed IDs that are no longer in the data file
    processed_ids = processed_ids.intersection(current_ids)

    # Filter to only include rows where Country is 'United States' and Customer Id is new
    df_customers_filtered = df_customers[
        (df_customers["Country"] == "United States") & 
        (~df_customers["Customer Id"].isin(processed_ids))
    ]

    if df_customers_filtered.empty:
        print("No new records to process.")
        save_processed_ids(processed_ids_file, processed_ids)  # Save updated processed IDs
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
    print(f"Total records in processed IDs: {len(processed_ids)}")

if __name__ == "__main__":
    process_new_records()

```

Here's an explanation of the changes made to the script:

1. After reading the customer data file, we create a set of all current customer IDs:
   ```python
   current_ids = set(df_customers["Customer Id"])
   ```

2. We then update the `processed_ids` set to only include IDs that are still present in the current data:
   ```python
   processed_ids = processed_ids.intersection(current_ids)
   ```

3. We've moved the saving of processed IDs to occur even if there are no new records to process. This ensures that obsolete IDs are removed even on days when no new records are processed:
   ```python
   if df_customers_filtered.empty:
       print("No new records to process.")
       save_processed_ids(processed_ids_file, processed_ids)  # Save updated processed IDs
       return
   ```

4. At the end of the script, we've added a print statement to show the total number of records in the processed IDs file after the update:
   ```python
   print(f"Total records in processed IDs: {len(processed_ids)}")
   ```

These changes ensure that:
- IDs of records that no longer appear in the data file are removed from the processed IDs list.
- The processed IDs file is updated every time the script runs, even if no new records are processed.
- You get feedback on how many IDs are in the processed list after each run.

This approach will keep your processed IDs list current and prevent it from growing indefinitely with obsolete IDs. The script will now efficiently handle both the addition of new records and the removal of old ones from the tracking system.
