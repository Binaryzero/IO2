import pandas as pd

# Read the lookup file into a DataFrame
df_lookup = pd.read_csv("city_lookup.csv")

# Read the customer data file into a DataFrame
df_customers = pd.read_csv("customers-10000.csv")

# Filter to only include rows where Country is 'United States'
df_customers_filtered = df_customers[df_customers["Country"] == "United States"]

# Merge the filtered customer DataFrame with the lookup DataFrame
df_merged = df_customers_filtered.merge(
    df_lookup[["City", "UUID", "ZIP Code", "Area Code"]], on="City", how="left"
)

# Combine 'First Name' and 'Last Name' into 'Legal Name'
df_merged["Legal Name"] = df_merged["First Name"] + " " + df_merged["Last Name"]

# Add a new column 'Reviewed' with the static text "Reviewed by Bob"
df_merged["Reviewed"] = "Reviewed by Bob"

# Apply the column mapping, including 'Legal Name', 'UUID', 'Reviewed' and excluding 'First Name', 'Last Name', 'City'
column_mapping = {
    "Customer Id": "ID",
    "Email": "email address",
    "Legal Name": "Legal Name",
    "UUID": "UUID",
    "Reviewed": "Reviewed",
    "ZIP Code": "ZIP Code",
    "Area Code": "Area Code"
}

# Iterate through unique cities and create a new file for each city
for city in df_merged["City"].unique():
    df_city = df_merged[df_merged["City"] == city]
    df_city_mapped = df_city[list(column_mapping.keys())].rename(columns=column_mapping)
    
    # Define the file name based on the city
    file_name = f"datavue_{city.replace(' ', '_').replace('/', '_')}.csv"
    
    # Write the DataFrame to a new CSV file
    df_city_mapped.to_csv(file_name, index=False)
    
    # Print a confirmation message for each city
    print(f"The final data for {city} has been written to '{file_name}'.")
