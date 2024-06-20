import pandas as pd

# Sample data for multiple days
day_1_data = {
    "Customer Id": [1, 2, 3],
    "First Name": ["John", "Jane", "Mike"],
    "Last Name": ["Doe", "Smith", "Johnson"],
    "Company": ["CompanyA", "CompanyB", "CompanyC"],
    "City": ["CityA", "CityB", "CityC"],
    "Country": ["USA", "Canada", "USA"],
    "Phone 1": ["123-456-7890", "123-456-7892", "123-456-7894"],
    "Phone 2": ["123-456-7891", "123-456-7893", "123-456-7895"],
    "Email": [
        "john.doe@example.com",
        "jane.smith@example.com",
        "mike.johnson@example.com",
    ],
    "Subscription Date": ["2021-01-01", "2021-01-02", "2021-01-03"],
    "Website": ["http://example.com", "http://example.com", "http://example.com"],
}

day_2_data = {
    "Customer Id": [4, 5, 3],
    "First Name": ["Alice", "Bob", "Mike"],
    "Last Name": ["Brown", "Davis", "Johnson"],
    "Company": ["CompanyD", "CompanyE", "CompanyC"],
    "City": ["CityD", "CityE", "CityC"],
    "Country": ["USA", "Canada", "USA"],
    "Phone 1": ["123-456-7896", "123-456-7898", "123-456-7894"],
    "Phone 2": ["123-456-7897", "123-456-7899", "123-456-7895"],
    "Email": [
        "alice.brown@example.com",
        "bob.davis@example.com",
        "mike.johnson@example.com",
    ],
    "Subscription Date": ["2021-01-04", "2021-01-05", "2021-01-03"],
    "Website": ["http://example.com", "http://example.com", "http://example.com"],
}

day_3_data = {
    "Customer Id": [6, 7, 5],
    "First Name": ["Charlie", "Dave", "Bob"],
    "Last Name": ["Wilson", "Green", "Davis"],
    "Company": ["CompanyF", "CompanyG", "CompanyE"],
    "City": ["CityF", "CityG", "CityE"],
    "Country": ["UK", "UK", "Canada"],
    "Phone 1": ["123-456-7800", "123-456-7802", "123-456-7898"],
    "Phone 2": ["123-456-7801", "123-456-7803", "123-456-7899"],
    "Email": [
        "charlie.wilson@example.com",
        "dave.green@example.com",
        "bob.davis@example.com",
    ],
    "Subscription Date": ["2021-01-06", "2021-01-07", "2021-01-05"],
    "Website": ["http://example.com", "http://example.com", "http://example.com"],
}

# Convert dictionaries to DataFrames and save as CSV files
day_1_df = pd.DataFrame(day_1_data)
day_1_df.to_csv("day_1_customers.csv", index=False)

day_2_df = pd.DataFrame(day_2_data)
day_2_df.to_csv("day_2_customers.csv", index=False)

day_3_df = pd.DataFrame(day_3_data)
day_3_df.to_csv("day_3_customers.csv", index=False)
