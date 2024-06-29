import requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
import tableauserverclient as TSC

# Tableau server information
server_url = 'https://your-tableau-server.com'
site_name = ''  # Leave empty for the default site
csv_export_url = 'https://your-tableau-server.com/views/your_view_name.csv'  # URL to export the CSV

# Create a Kerberos authentication object
kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)

# Send a GET request to the CSV export URL with Kerberos authentication
response = requests.get(csv_export_url, auth=kerberos_auth)

# Ensure the request was successful
if response.status_code == 200:
    # Open a local file with write-binary mode and save the CSV content
    with open('downloaded_file.csv', 'wb') as file:
        file.write(response.content)
    print("CSV file downloaded successfully.")
else:
    print("Failed to download CSV file. Status code:", response.status_code)
