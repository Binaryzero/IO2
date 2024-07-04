Certainly! I'll provide you with the full, complete file that includes all the necessary functions and the main execution flow. This script will generate a security vulnerability report with an executive summary and send it via Outlook.



```python
import csv
from collections import Counter
from datetime import datetime, timedelta
import win32com.client

def read_csv_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_priority_data(data, priority):
    return [row for row in data if row['Priority'] == f'priority {priority}']

def get_top_vulnerable_servers(data, priority, top_n=5):
    priority_data = get_priority_data(data, priority)
    server_counter = Counter(row['Host'] for row in priority_data)
    return server_counter.most_common(top_n)

def get_due_date_outlook(data, priority):
    priority_data = get_priority_data(data, priority)
    today = datetime.now().date()
    due_dates = [datetime.strptime(row['Due Date'], '%Y-%m-%d').date() for row in priority_data]
    
    time_frames = [10, 30, 45, 60, 100, 180]
    due_within_periods = {days: sum(1 for date in due_dates if (date - today).days <= days) for days in time_frames}
    
    total_vulnerabilities = len(priority_data)
    return {days: (count, count/total_vulnerabilities if total_vulnerabilities else 0) 
            for days, count in due_within_periods.items()}

def generate_executive_summary(data):
    total_vulnerabilities = len(data)
    affected_servers = len(set(row['Host'] for row in data))
    priority_count = Counter(row['Priority'] for row in data)
    
    # Get the top 3 most critical vulnerabilities
    critical_vulnerabilities = [row for row in data if row['Priority'] == 'priority 1']
    top_critical = Counter(row['Title'] for row in critical_vulnerabilities).most_common(3)
    
    # Get the nearest due date
    nearest_due_date = min(datetime.strptime(row['Due Date'], '%Y-%m-%d').date() for row in data)
    
    summary = f"""
    <h2>Executive Summary</h2>
    <p>This report identifies {total_vulnerabilities} unique vulnerabilities across {affected_servers} servers.</p>
    <ul>
        <li>High Priority (P1): {priority_count['priority 1']} ({priority_count['priority 1']/total_vulnerabilities:.1%})</li>
        <li>Medium Priority (P2): {priority_count['priority 2']} ({priority_count['priority 2']/total_vulnerabilities:.1%})</li>
        <li>Low Priority (P3): {priority_count['priority 3']} ({priority_count['priority 3']/total_vulnerabilities:.1%})</li>
    </ul>
    <p>Top 3 critical vulnerabilities:</p>
    <ol>
    """
    
    for vuln, count in top_critical:
        summary += f"<li>{vuln} ({count} instances)</li>"
    
    summary += f"""
    </ol>
    <p>Nearest due date for remediation: {nearest_due_date.strftime('%Y-%m-%d')}</p>
    <p>Immediate action is required to address high-priority vulnerabilities and those with imminent due dates.</p>
    """
    
    return summary

def generate_html_report(data):
    executive_summary = generate_executive_summary(data)
    
    total_vulnerabilities = len(data)
    affected_servers = len(set(row['Host'] for row in data))
    
    vulnerability_counter = Counter(row['Title'] for row in data)
    priority_count = Counter(row['Priority'] for row in data)
    
    # Most common vulnerabilities
    most_common_vulnerabilities = vulnerability_counter.most_common(5)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Security Vulnerability Summary Report</h1>

        {executive_summary}

        <hr>

        <h2>Detailed Report</h2>

        <h3>Key Statistics</h3>
        <ul>
            <li>Total vulnerabilities: {total_vulnerabilities}</li>
            <li>Affected servers: {affected_servers}</li>
            <li>Priority breakdown:
                <ul>
                    <li>Priority 1 (High): {priority_count['priority 1']} ({priority_count['priority 1']/total_vulnerabilities:.1%})</li>
                    <li>Priority 2 (Medium): {priority_count['priority 2']} ({priority_count['priority 2']/total_vulnerabilities:.1%})</li>
                    <li>Priority 3 (Low): {priority_count['priority 3']} ({priority_count['priority 3']/total_vulnerabilities:.1%})</li>
                </ul>
            </li>
        </ul>

        <h3>Most Common Vulnerabilities</h3>
        {generate_html_list(most_common_vulnerabilities)}

        <h3>Servers with Most Vulnerabilities (by Priority)</h3>
    """

    for priority in range(1, 4):
        top_servers = get_top_vulnerable_servers(data, priority)
        html += f"<h4>Priority {priority}</h4>"
        if top_servers:
            html += generate_html_list(top_servers)
        else:
            html += "<p>No vulnerabilities found for this priority.</p>"

    html += "<h3>Upcoming Due Dates (by Priority)</h3>"

    for priority in range(1, 4):
        due_date_outlook = get_due_date_outlook(data, priority)
        html += f"<h4>Priority {priority}</h4>"
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            html += "<table><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>"
            for days, (count, percentage) in due_date_outlook.items():
                html += f"<tr><td>{days}-day outlook</td><td>{count}</td><td>{percentage:.1%}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No vulnerabilities found for this priority.</p>"

    html += """
        <h3>Recommendations</h3>
        <ol>
            <li>Prioritize patching for Priority 1 vulnerabilities, especially those due within the next 30 days.</li>
            <li>Address Priority 2 vulnerabilities on a regular schedule, focusing on those due within 60 days.</li>
            <li>Implement a regular patching schedule for Priority 3 vulnerabilities to maintain overall system health.</li>
            <li>Conduct thorough security assessments on the top vulnerable servers identified for each priority level.</li>
            <li>Enhance security measures against prevalent attack vectors identified in the most common vulnerabilities list.</li>
        </ol>

        <p>This summary provides a high-level overview of the current security posture. For detailed information on specific vulnerabilities or affected servers, please refer to the full vulnerability report.</p>
    </body>
    </html>
    """
    return html

def generate_html_list(items):
    return "<ol>" + "".join(f"<li>{item[0]}: {item[1]} instances</li>" for item in items) + "</ol>"

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

This complete script includes all necessary functions to:

1. Read and process the CSV data
2. Generate an executive summary
3. Create a detailed HTML report
4. Send the report via Outlook

To use this script:

1. Save it as a Python file (e.g., `security_report_generator.py`).

2. Install the required library by running:
   ```
   pip install pywin32
   ```

3. Update the following variables in the script:
   - `csv_file_path`: Set this to the path of your CSV file containing the vulnerability data.
   - `email_recipients`: Add the email addresses of the recipients who should receive the report.

4. Ensure Outlook is installed and configured on your Windows machine.

5. Run the script using:
   ```
   python security_report_generator.py
   ```

The script will generate a comprehensive security vulnerability report with an executive summary, save it as an HTML file, and send it via Outlook to the specified recipients.

This all-in-one script provides a complete solution for generating and distributing your security vulnerability reports, making it easy to keep stakeholders informed about the current security posture of your systems.
