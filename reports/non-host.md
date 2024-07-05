Thank you for the additional requirements. I'll update the script to accommodate these changes. Let's modify the relevant parts of the script to implement these new features.

First, let's update the `get_host_or_source` function and create a new function to check if a vulnerability is a non-server vulnerability:



```python
import csv
from collections import Counter
from datetime import datetime
import win32com.client
from config import *

# ... [previous functions remain the same] ...

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

def generate_executive_summary(data):
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    
    top_app_ids = app_id_count.most_common(TOP_APP_IDS_COUNT)
    
    nearest_due_date = min(parse_date(row[COLUMN_DUE_DATE]) for row in data)
    
    summary = f"""
    <h2>Executive Summary</h2>
    <p>This report covers {total_vulnerabilities} total vulnerabilities, including {unique_vulnerabilities} unique vulnerabilities across {affected_hosts} hosts/sources.</p>
    <ul>
    """
    
    for priority in PRIORITY_LEVELS:
        count = priority_count[priority]
        summary += f"<li>{priority}: {count} ({count/total_vulnerabilities:.1%})</li>"
    
    summary += """
    </ul>
    <p>Top Applications by vulnerability count:</p>
    <ul>
    """
    
    for app_id, count in top_app_ids:
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        priority_breakdown = " | ".join(f"{priority}: {app_priority_count[priority]}" for priority in PRIORITY_LEVELS)
        summary += f"<li>{app_name} (ID: {app_id}): {count} vulnerabilities ({priority_breakdown})</li>"
    
    summary += f"""
    </ul>
    <p>Nearest due date for remediation: {nearest_due_date.strftime('%Y-%m-%d')}</p>
    <p>Immediate action is required to address high-priority vulnerabilities and those with imminent due dates.</p>
    """
    
    return summary

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
    for priority in PRIORITY_LEVELS:
        top_hosts = get_top_vulnerable_hosts(data, priority)
        vulnerable_hosts_by_priority += f"<h4>{priority}</h4>"
        if top_hosts:
            vulnerable_hosts_by_priority += generate_html_list(top_hosts)
        else:
            vulnerable_hosts_by_priority += "<p>No vulnerabilities found for this priority.</p>"
        
        due_date_outlook = get_due_date_outlook(data, priority)
        due_dates_by_priority += f"<h4>{priority}</h4>"
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            due_dates_by_priority += "<table><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>"
            for days, (count, percentage) in due_date_outlook.items():
                due_dates_by_priority += f"<tr><td>{days}-day outlook</td><td>{count}</td><td>{percentage:.1%}</td></tr>"
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
        for priority in PRIORITY_LEVELS:
            vulnerabilities_by_app += f"<li>{priority}: {app_priority_count[priority]}</li>"
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

# ... [rest of the script remains the same] ...

```

Key changes in this update:

1. Modified `get_host_or_source()` to return "Non-Server Vuln" when both Host Name / Server and Sources are null.
2. Added `is_non_server_vuln()` function to check if a vulnerability is a non-server vulnerability.
3. Updated `get_top_vulnerable_hosts()` to exclude non-server vulnerabilities.
4. Modified the executive summary in `generate_executive_summary()` to list applications with their severity risk breakdown on one line.
5. Updated the affected hosts count to exclude non-server vulnerabilities.

These changes will:
- Use "Non-Server Vuln" when both Host Name / Server and Sources are null.
- Exclude non-server vulnerabilities from the Host Names report.
- Update the executive summary to list applications with their severity risk breakdown on one line.

To use this updated version:

1. Replace your existing Python script with this new version.
2. Ensure that your `config.py`, `report_template.html`, and `report_styles.css` files are up to date and in the correct locations.
3. Run the script as before.

This updated script should now meet all the new requirements you've specified, providing a more accurate and detailed report of your vulnerabilities, including proper handling of non-server vulnerabilities and a more concise executive summary.
