Absolutely! Separating the formatting from the main script is a great way to improve maintainability and make editing easier. We can store the HTML template and CSS in separate files and then load them into the script when needed. Here's how we can modify the script to achieve this:

1. First, let's create two new files:



```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Summary Report</title>
    <style>
        {styles}
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
        <li>Affected host names: {affected_servers}</li>
        <li>Priority breakdown:
            <ul>
                <li>Priority 1 (High): {priority_1_count} ({priority_1_percentage:.1%})</li>
                <li>Priority 2 (Medium): {priority_2_count} ({priority_2_percentage:.1%})</li>
                <li>Priority 3 (Low): {priority_3_count} ({priority_3_percentage:.1%})</li>
            </ul>
        </li>
    </ul>

    <h3>Most Common Vulnerabilities</h3>
    {most_common_vulnerabilities}

    <h3>Host Names with Most Vulnerabilities (by Priority)</h3>
    {vulnerable_servers_by_priority}

    <h3>Upcoming Due Dates (by Priority)</h3>
    {due_dates_by_priority}

    <h3>Recommendations</h3>
    <ol>
        <li>Prioritize patching for Priority 1 vulnerabilities, especially those due within the next 30 days.</li>
        <li>Address Priority 2 vulnerabilities on a regular schedule, focusing on those due within 60 days.</li>
        <li>Implement a regular patching schedule for Priority 3 vulnerabilities to maintain overall system health.</li>
        <li>Conduct thorough security assessments on the top vulnerable host names identified for each priority level.</li>
        <li>Enhance security measures against prevalent attack vectors identified in the most common vulnerabilities list.</li>
    </ol>

    <p>This summary provides a high-level overview of the current security posture. For detailed information on specific vulnerabilities or affected host names, please refer to the full vulnerability report.</p>
</body>
</html>

```

```plaintext
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
h1 {
    color: #2c3e50;
}
h2 {
    color: #34495e;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
}

```

Now, let's update the main script to use these external files:

```python
import csv
from collections import Counter
from datetime import datetime, timedelta
import win32com.client

def read_csv_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def parse_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

def get_priority_data(data, priority):
    return [row for row in data if row['Severity Risk'] == f'priority {priority}']

def get_top_vulnerable_servers(data, priority, top_n=5):
    priority_data = get_priority_data(data, priority)
    server_counter = Counter(row['Host Name / Server'] for row in priority_data)
    return server_counter.most_common(top_n)

def get_due_date_outlook(data, priority):
    priority_data = get_priority_data(data, priority)
    today = datetime.now()
    due_dates = [parse_date(row['Due Date']) for row in priority_data]
    
    time_frames = [10, 30, 45, 60, 100, 180]
    due_within_periods = {days: sum(1 for date in due_dates if (date - today).days <= days) for days in time_frames}
    
    total_vulnerabilities = len(priority_data)
    return {days: (count, count/total_vulnerabilities if total_vulnerabilities else 0) 
            for days, count in due_within_periods.items()}

def generate_executive_summary(data):
    total_vulnerabilities = len(data)
    affected_servers = len(set(row['Host Name / Server'] for row in data))
    priority_count = Counter(row['Severity Risk'] for row in data)
    
    critical_vulnerabilities = [row for row in data if row['Severity Risk'] == 'priority 1']
    top_critical = Counter(row['Title'] for row in critical_vulnerabilities).most_common(3)
    
    nearest_due_date = min(parse_date(row['Due Date']) for row in data)
    
    summary = f"""
    <h2>Executive Summary</h2>
    <p>This report identifies {total_vulnerabilities} unique vulnerabilities across {affected_servers} host names.</p>
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

def generate_html_list(items):
    return "<ol>" + "".join(f"<li>{item[0]}: {item[1]} instances</li>" for item in items) + "</ol>"

def generate_html_report(data):
    with open('report_template.html', 'r') as f:
        template = f.read()
    
    with open('report_styles.css', 'r') as f:
        styles = f.read()
    
    total_vulnerabilities = len(data)
    affected_servers = len(set(row['Host Name / Server'] for row in data))
    priority_count = Counter(row['Severity Risk'] for row in data)
    
    vulnerability_counter = Counter(row['Title'] for row in data)
    most_common_vulnerabilities = generate_html_list(vulnerability_counter.most_common(5))
    
    vulnerable_servers_by_priority = ""
    due_dates_by_priority = ""
    for priority in range(1, 4):
        top_servers = get_top_vulnerable_servers(data, priority)
        vulnerable_servers_by_priority += f"<h4>Priority {priority}</h4>"
        if top_servers:
            vulnerable_servers_by_priority += generate_html_list(top_servers)
        else:
            vulnerable_servers_by_priority += "<p>No vulnerabilities found for this priority.</p>"
        
        due_date_outlook = get_due_date_outlook(data, priority)
        due_dates_by_priority += f"<h4>Priority {priority}</h4>"
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            due_dates_by_priority += "<table><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>"
            for days, (count, percentage) in due_date_outlook.items():
                due_dates_by_priority += f"<tr><td>{days}-day outlook</td><td>{count}</td><td>{percentage:.1%}</td></tr>"
            due_dates_by_priority += "</table>"
        else:
            due_dates_by_priority += "<p>No vulnerabilities found for this priority.</p>"
    
    return template.format(
        styles=styles,
        executive_summary=generate_executive_summary(data),
        total_vulnerabilities=total_vulnerabilities,
        affected_servers=affected_servers,
        priority_1_count=priority_count['priority 1'],
        priority_1_percentage=priority_count['priority 1']/total_vulnerabilities,
        priority_2_count=priority_count['priority 2'],
        priority_2_percentage=priority_count['priority 2']/total_vulnerabilities,
        priority_3_count=priority_count['priority 3'],
        priority_3_percentage=priority_count['priority 3']/total_vulnerabilities,
        most_common_vulnerabilities=most_common_vulnerabilities,
        vulnerable_servers_by_priority=vulnerable_servers_by_priority,
        due_dates_by_priority=due_dates_by_priority
    )

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
    csv_file_path = 'path_to_your_csv_file.csv'
    email_recipients = ['recipient1@example.com', 'recipient2@example.com']
    email_subject = 'Security Vulnerability Summary Report'

    data = read_csv_data(csv_file_path)
    report_html = generate_html_report(data)
    
    with open('security_report.html', 'w') as f:
        f.write(report_html)
    
    try:
        send_outlook_email(email_subject, report_html, email_recipients)
        print("Report sent successfully via Outlook!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        print("The report has been saved as 'security_report.html' in the current directory.")

    print("Process completed.")

```

This updated script does the following:

1. It uses external files for the HTML template (`report_template.html`) and CSS styles (`report_styles.css`).
2. The `generate_html_report()` function now loads these external files and uses string formatting to populate the template with data.
3. The main logic of the script remains the same, but the HTML generation is now more modular and easier to maintain.

To use this updated version:

1. Save the HTML template as `report_template.html` and the CSS as `report_styles.css` in the same directory as your Python script.
2. Update the Python script as shown above and save it (e.g., as `security_report_generator.py`).
3. Ensure you have the `pywin32` library installed (`pip install pywin32`).
4. Update the `csv_file_path` and `email_recipients` variables in the script.
5. Run the script using `python security_report_generator.py`.

This approach makes it much easier to edit the report's layout and styling without having to modify the Python code. You can now update the HTML structure in `report_template.html` and the styles in `report_styles.css` without touching the main script.
