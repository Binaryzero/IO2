import os
from datetime import datetime

import pandas as pd

# Paths to your files
accumulated_file_path = "accumulated_customers.csv"
output_file_path = "sorted_new_customers_by_country.csv"
seen_countries_file_path = "seen_countries.txt"
summary_file_path = "summary_of_changes.csv"


# Function to process data for a given day
def process_daily_data(new_data_file_path):
    # Load the accumulated data
    try:
        accumulated_data = pd.read_csv(accumulated_file_path)
    except FileNotFoundError:
        accumulated_data = (
            pd.DataFrame()
        )  # If the file does not exist, create an empty DataFrame

    # Load the new data
    new_data = pd.read_csv(new_data_file_path)

    # Load the set of seen countries
    if os.path.exists(seen_countries_file_path):
        with open(seen_countries_file_path, "r") as file:
            seen_countries = set(file.read().splitlines())
    else:
        seen_countries = set()

    # Identify new records by comparing the new data with the accumulated data
    if not accumulated_data.empty:
        new_records = new_data[
            ~new_data["Customer Id"].isin(accumulated_data["Customer Id"])
        ]
        carryover_records = new_data[
            new_data["Customer Id"].isin(accumulated_data["Customer Id"])
        ]
        deleted_records = accumulated_data[
            ~accumulated_data["Customer Id"].isin(new_data["Customer Id"])
        ]
    else:
        new_records = new_data
        carryover_records = pd.DataFrame()
        deleted_records = pd.DataFrame()

    # Combine carryover records and new records to form the updated accumulated data
    updated_accumulated_data = pd.concat(
        [carryover_records, new_records]
    ).drop_duplicates()

    # Sort the new records by 'Country'
    sorted_new_records = new_records.sort_values(by="Country")

    # Prepare a new list to hold the transformed data
    output_data = []

    # Get the unique countries in the new data
    new_countries = sorted_new_records["Country"].unique()

    # Get the unique countries in the accumulated data
    existing_countries = (
        carryover_records["Country"].unique() if not carryover_records.empty else []
    )

    # Iterate over each unique country and add the country name row if it is a new country
    for country in new_countries:
        if country not in seen_countries:
            output_data.append({"Country": f"Here are all the records for {country}"})
            seen_countries.add(country)  # Update the set of seen countries
        country_data = sorted_new_records[sorted_new_records["Country"] == country]
        output_data.extend(country_data.to_dict(orient="records"))

    # Convert the output data back to a DataFrame
    output_df = pd.DataFrame(output_data)

    # Save the transformed data to a new CSV file
    output_df.to_csv(output_file_path, index=False)

    # Save the updated accumulated data
    updated_accumulated_data.to_csv(accumulated_file_path, index=False)

    # Save the set of seen countries
    with open(seen_countries_file_path, "w") as file:
        for country in seen_countries:
            file.write(f"{country}\n")

    # Prepare the summary of changes with a date stamp
    today = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "Date": today,
        "New Records": len(new_records),
        "Carryover Records": len(carryover_records),
        "Deleted Records": len(deleted_records),
    }

    # Convert summary to a DataFrame
    summary_df = pd.DataFrame([summary])

    # Save the summary to a CSV file, appending if the file exists
    if os.path.exists(summary_file_path):
        summary_df.to_csv(summary_file_path, mode="a", header=False, index=False)
    else:
        summary_df.to_csv(summary_file_path, index=False)

    print(f"Processed data from {new_data_file_path}")
    print(f"Transformed data saved to {output_file_path}")
    print(f"Accumulated data updated at {accumulated_file_path}")
    print(f"Seen countries updated at {seen_countries_file_path}")
    print(f"Summary of changes saved to {summary_file_path}")


# Simulate running the script for each day
for day in range(1, 4):
    new_data_file_path = f"day_{day}_customers.csv"
    process_daily_data(new_data_file_path)
