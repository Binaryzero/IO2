Certainly! I'll modify the script to use the Outlook COM object to automatically create and send an email with the HTML report as its body. This approach works well on Windows machines with Outlook installed.

Here's an updated version of the script that automates the email creation and sending process:



```python
import csv
from collections import Counter
from datetime import datetime, timedelta
import win32com.client

# [All previous functions for data processing and HTML generation remain the same]

def send_outlook_email(subject, body, recipients):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    message = outlook.Application.CreateItem(0)
    message.Subject = subject
    message.HTMLBody = body
    
    if isinstance(recipients, str):
        recipients = [recipients]
    
    for recipient in recipients:
        message.Recipients.Add(recipient)
    
    message.Send()
    print(f"Email sent to: {', '.join(recipients)}")

def generate_html_report(data):
    # [The content of this function remains the same as in the previous version]
    # ...
    return html

if __name__ == "__main__":
    # Configuration
    csv_file_path = 'path_to_your_csv_file.csv'
    email_recipients = ['recipient1@example.com', 'recipient2@example.com']  # Add your recipients here
    email_subject = 'Security Vulnerability Summary Report'

    # Read data and generate report
    data = read_csv_data(csv_file_path)
    report_html = generate_html_report(data)
    
    # Save report to file (optional)
    with open('security_report.html', 'w') as f:
        f.write(report_html)
    
    # Send email
    try:
        send_outlook_email(email_subject, report_html, email_recipients)
        print("Report sent successfully via Outlook!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        print("The report has been saved as 'security_report.html' in the current directory.")

    print("Process completed.")

```

To use this automated script:

1. Save it as a Python file (e.g., `send_security_report.py`).

2. Ensure you have the required libraries installed. You may need to run:
   ```
   pip install pywin32
   ```

3. Update the following variables in the script:
   - `csv_file_path`: Set this to the path of your CSV file containing the vulnerability data.
   - `email_recipients`: Add the email addresses of the recipients who should receive the report.

4. Make sure Outlook is installed on your Windows machine and that you're logged in.

5. Run the script using a command like: `python send_security_report.py`

The script will:
1. Read the CSV data
2. Generate the HTML report
3. Save the report as an HTML file (for backup purposes)
4. Create a new email in Outlook with the HTML report as its body
5. Send the email to the specified recipients

Important notes:

1. This script uses the Outlook COM object, so it will only work on Windows machines with Outlook installed and configured.

2. The script will use your default Outlook profile to send the email. Make sure you're logged into the correct account in Outlook.

3. Some organizations have security policies that might prevent scripts from automatically sending emails. If you encounter issues, you may need to check with your IT department.

4. Always test the script by sending to your own email address first before sending to others.

5. You might want to add error handling and logging for production use.

6. If you plan to run this script regularly, you could set it up as a scheduled task in Windows Task Scheduler.

This automated approach eliminates the need for manual copying and pasting, making the reporting process more efficient and less prone to human error. The report will be sent directly from your Outlook account, maintaining any corporate email signatures or formatting you might have set up.
