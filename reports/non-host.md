Certainly! I'll provide you with all the files needed for the complete security vulnerability report generator. This will include the main Python script, the configuration file, the HTML template, and the CSS file.

1. Main Python Script (security_report_generator.py):

```python
import csv
from collections import Counter
from datetime import datetime, timedelta
import win32com.client
from config import *

def read_csv_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def parse_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

def get_priority_data(data, priority):
    return [row for row in data if row[COLUMN_SEVERITY_RISK] == priority]

def get_host_or_source(row):
    if row[COLUMN_HOST_NAME] or row[COLUMN_SOURCES]:
        return row[COLUMN_HOST_NAME] or row[COLUMN_SOURCES]
    return "Non-Server Vuln"

def is_non_server_vuln(row):
    return not (row[COLUMN_HOST_NAME] or row[COLUMN_SOURCES])

def get_top_vulnerable_hosts(data, priority, top_n=TOP_SERVERS_COUNT):
    priority_data = get_priority_data(data, priority)
    host_counter = Counter(get_host_or_source(row) for row in priority_data if not is_non_server_vuln(row))
    return host_counter.most_common(top_n)

def get_due_date_outlook(data, priority):
    priority_data = get_priority_data(data, priority)
    today = datetime.now().date()
    due_dates = [parse_date(row[COLUMN_DUE_DATE]).date() for row in priority_data]
    
    past_due = sum(1 for date in due_dates if date < today)
    due_today = sum(1 for date in due_dates if date == today)
    
    due_within_periods = {days: sum(1 for date in due_dates if 0 <= (date - today).days <= days) for days in DUE_DATE_TIME_FRAMES}
    
    total_vulnerabilities = len(priority_data)
    result = {
        'past_due': (past_due, past_due/total_vulnerabilities if total_vulnerabilities else 0),
        'due_today': (due_today, due_today/total_vulnerabilities if total_vulnerabilities else 0)
    }
    result.update({days: (count, count/total_vulnerabilities if total_vulnerabilities else 0) 
                   for days, count in due_within_periods.items()})
    
    return result

def generate_executive_summary(data):
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    
    top_app_ids = app_id_count.most_common(TOP_APP_IDS_COUNT)
    
    today = datetime.now().date()
    past_due = sum(1 for row in data if parse_date(row[COLUMN_DUE_DATE]).date() < today)
    
    summary = f"""
    <h2>Executive Summary</h2>
    <p>This report covers {total_vulnerabilities} total vulnerabilities, including {unique_vulnerabilities} unique vulnerabilities across {affected_hosts} hosts/sources.</p>
    <p><strong class="priority-high">Past Due Vulnerabilities: {past_due}</strong></p>
    <ul>
    """
    
    for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
        count = priority_count[priority]
        summary += f'<li class="{class_name}">{priority}: {count} ({count/total_vulnerabilities:.1%})</li>'
    
    summary += """
    </ul>
    <p>Top Applications by vulnerability count:</p>
    <ul>
    """
    
    for app_id, count in top_app_ids:
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        priority_breakdown = " | ".join(f'<span class="{class_name}">{priority}: {app_priority_count[priority]}</span>' 
                                        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']))
        summary += f"""<li>
            <div class="app-name">{app_name} (ID: {app_id}): {count} vulnerabilities</div>
            <div class="severity-breakdown">{priority_breakdown}</div>
        </li>"""
    
    summary += f"""
    </ul>
    <p>Immediate action is required to address past due and high-priority vulnerabilities.</p>
    """
    
    return summary

def generate_html_list(items):
    return "<ol>" + "".join(f"<li>{item[0]}: {item[1]} instances</li>" for item in items) + "</ol>"

def generate_html_report(data):
    with open(HTML_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    with open(CSS_STYLE_PATH, 'r') as f:
        styles = f.read()
    
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    
    vulnerability_counter = Counter(row[COLUMN_TITLE] for row in data)
    most_common_vulnerabilities = generate_html_list(vulnerability_counter.most_common(TOP_VULNERABILITIES_COUNT))
    
    vulnerable_hosts_by_priority = ""
    due_dates_by_priority = ""
    for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
        top_hosts = get_top_vulnerable_hosts(data, priority)
        vulnerable_hosts_by_priority += f'<h4 class="{class_name}">{priority}</h4>'
        if top_hosts:
            vulnerable_hosts_by_priority += generate_html_list(top_hosts)
        else:
            vulnerable_hosts_by_priority += "<p>No vulnerabilities found for this priority.</p>"
        
        due_date_outlook = get_due_date_outlook(data, priority)
        due_dates_by_priority += f'<h4 class="{class_name}">{priority}</h4>'
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            due_dates_by_priority += '<table><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>'
            if 'past_due' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-high"><td>Past Due</td><td>{due_date_outlook["past_due"][0]}</td><td>{due_date_outlook["past_due"][1]:.1%}</td></tr>'
            if 'due_today' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-high"><td>Due Today</td><td>{due_date_outlook["due_today"][0]}</td><td>{due_date_outlook["due_today"][1]:.1%}</td></tr>'
            for days, (count, percentage) in due_date_outlook.items():
                if days in DUE_DATE_TIME_FRAMES:
                    due_dates_by_priority += f'<tr><td>Next {days} days</td><td>{count}</td><td>{percentage:.1%}</td></tr>'
            due_dates_by_priority += "</table>"
        else:
            due_dates_by_priority += "<p>No vulnerabilities found for this priority.</p>"
    
    vulnerabilities_by_app = ""
    for app_id, count in app_id_count.most_common():
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        vulnerabilities_by_app += f"<h4>{app_name} (ID: {app_id})</h4>"
        vulnerabilities_by_app += f"<p>Total vulnerabilities: {count}</p>"
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        vulnerabilities_by_app += "<ul>"
        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
            vulnerabilities_by_app += f'<li class="{class_name}">{priority}: {app_priority_count[priority]}</li>'
        vulnerabilities_by_app += "</ul>"
    
    return template.format(
        styles=styles,
        executive_summary=generate_executive_summary(data),
        total_vulnerabilities=total_vulnerabilities,
        unique_vulnerabilities=unique_vulnerabilities,
        affected_hosts=affected_hosts,
        priority_1_count=priority_count[PRIORITY_LEVELS[0]],
        priority_1_percentage=priority_count[PRIORITY_LEVELS[0]]/total_vulnerabilities,
        priority_2_count=priority_count[PRIORITY_LEVELS[1]],
        priority_2_percentage=priority_count[PRIORITY_LEVELS[1]]/total_vulnerabilities,
        priority_3_count=priority_count[PRIORITY_LEVELS[2]],
        priority_3_percentage=priority_count[PRIORITY_LEVELS[2]]/total_vulnerabilities,
        most_common_vulnerabilities=most_common_vulnerabilities,
        vulnerable_hosts_by_priority=vulnerable_hosts_by_priority,
        due_dates_by_priority=due_dates_by_priority,
        vulnerabilities_by_app=vulnerabilities_by_app
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
    data = read_csv_data(CSV_FILE_PATH)
    report_html = generate_html_report(data)
    
    with open(OUTPUT_REPORT_PATH, 'w') as f:
        f.write(report_html)
    
    try:
        send_outlook_email(EMAIL_SUBJECT, report_html, EMAIL_RECIPIENTS)
        print("Report sent successfully via Outlook!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        print(f"The report has been saved as '{OUTPUT_REPORT_PATH}' in the current directory.")

    print("Process completed.")

```

2. Configuration File (config.py):

```python
# File paths
CSV_FILE_PATH = 'path_to_your_csv_file.csv'
HTML_TEMPLATE_PATH = 'report_template.html'
CSS_STYLE_PATH = 'report_styles.css'
OUTPUT_REPORT_PATH = 'security_report.html'

# Email settings
EMAIL_RECIPIENTS = ['recipient1@example.com', 'recipient2@example.com']
EMAIL_SUBJECT = 'Security Vulnerability Summary Report'

# Report settings
TOP_VULNERABILITIES_COUNT = 5
TOP_SERVERS_COUNT = 5
TOP_APP_IDS_COUNT = 5

# Time frames for due date outlook (in days)
DUE_DATE_TIME_FRAMES = [10, 30, 45, 60, 100, 180]

# Column names
COLUMN_SEVERITY_RISK = 'Severity Risk'
COLUMN_APPLICATION_ID = 'Application ID'
COLUMN_APPLICATION_FULL_NAME = 'Application Full Name'
COLUMN_HOST_NAME = 'Host Name / Server'
COLUMN_SOURCES = 'Sources'
COLUMN_TITLE = 'Title'
COLUMN_DUE_DATE = 'Due Date'

# Priority levels
PRIORITY_LEVELS = ['Priority 1', 'Priority 2', 'Priority 3']

```

3. HTML Template (report_template.html):

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

    <div class="executive-summary">
        {executive_summary}
    </div>

    <hr>

    <h2>Detailed Report</h2>

    <div class="stat-box">
        <h3>Key Statistics</h3>
        <ul>
            <li>Total vulnerabilities: {total_vulnerabilities}</li>
            <li>Unique vulnerabilities: {unique_vulnerabilities}</li>
            <li>Affected host names: {affected_hosts}</li>
            <li>Priority breakdown:
                <ul>
                    <li class="priority-high">Priority 1 (High): {priority_1_count} ({priority_1_percentage:.1%})</li>
                    <li class="priority-medium">Priority 2 (Medium): {priority_2_count} ({priority_2_percentage:.1%})</li>
                    <li class="priority-low">Priority 3 (Low): {priority_3_count} ({priority_3_percentage:.1%})</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="stat-box">
        <h3>Most Common Vulnerabilities</h3>
        {most_common_vulnerabilities}
    </div>

    <div class="stat-box">
        <h3>Host Names with Most Vulnerabilities (by Priority)</h3>
        {vulnerable_hosts_by_priority}
    </div>

    <div class="stat-box">
        <h3>Upcoming Due Dates (by Priority)</h3>
        {due_dates_by_priority}
    </div>

    <div class="stat
```
