import tableauserverclient as TSC
import requests

# Tableau server information
server_url = 'https://your-tableau-server.com'
site_name = ''  # Leave empty for the default site
username = 'your-username'
password = 'your-password'
csv_export_url = 'https://your-tableau-server.com/views/your_view_name.csv'  # URL to export the CSV

# Sign in to the Tableau Server
tableau_auth = TSC.TableauAuth(username, password, site_name)
server = TSC.Server(server_url, use_server_version=True)

with server.auth.sign_in(tableau_auth):
    # Send a GET request to the CSV export URL
    response = requests.get(csv_export_url, auth=(username, password))
    
    # Ensure the request was successful
    if response.status_code == 200:
        # Open a local file with write-binary mode and save the CSV content
        with open('downloaded_file.csv', 'wb') as file:
            file.write(response.content)
        print("CSV file downloaded successfully.")
    else:
        print("Failed to download CSV file. Status code:", response.status_code)
