Certainly! I'll update the script to make these changes. We'll modify the executive summary formatting and apply the color coding throughout the report. Here's the updated version of the script:



First, let's update the CSS to include color coding for priorities:

```plaintext
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f0f4f8;
}

h1 {
    color: #2c3e50;
    background-color: #ecf0f1;
    padding: 10px;
    border-bottom: 3px solid #3498db;
}

h2 {
    color: #34495e;
    border-bottom: 2px solid #3498db;
    padding-bottom: 5px;
}

h3 {
    color: #2980b9;
}

h4 {
    color: #16a085;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
    background-color: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

th, td {
    border: 1px solid #bdc3c7;
    padding: 12px;
    text-align: left;
}

th {
    background-color: #3498db;
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f2f2f2;
}

ul, ol {
    background-color: #fff;
    padding: 15px 15px 15px 30px;
    border-radius: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

li {
    margin-bottom: 5px;
}

.executive-summary {
    background-color: #e8f4fd;
    border-left: 5px solid #3498db;
    padding: 15px;
    margin-bottom: 20px;
}

.priority-high {
    color: #c0392b;
}

.priority-medium {
    color: #d35400;
}

.priority-low {
    color: #27ae60;
}

.stat-box {
    background-color: #fff;
    border: 1px solid #bdc3c7;
    border-radius: 5px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-box h3 {
    margin-top: 0;
    border-bottom: 1px solid #ecf0f1;
    padding-bottom: 10px;
}

.app-name {
    font-weight: bold;
    margin-bottom: 5px;
}

.severity-breakdown {
    font-size: 0.9em;
    margin-left: 20px;
    color: #7f8c8d;
}

```

Now, let's update the main script to incorporate these changes:

```python
import csv
from collections import Counter
from datetime import datetime, timedelta
import win32com.client
from config import *

# ... [previous functions remain the same] ...

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
            due_dates_by_priority += f'<tr class="priority-high"><td>Past Due</td><td>{due_date_outlook["past_due"][0]}</td><td>{due_date_outlook["past_due"][1]:.1%}</td></tr>'
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

# ... [rest of the script remains the same] ...

```

Key changes in this update:

1. Updated the CSS to include new classes for formatting the executive summary and applying consistent color coding.
2. Modified the `generate_executive_summary()` function to:
   - Move the severity breakdown under the application names.
   - Use smaller font for the severity breakdown.
   - Apply color coding to priority levels.
3. Updated the `generate_html_report()` function to apply color coding consistently throughout the report.

To use this updated version:

1. Replace your existing Python script with this new version.
2. Update your `report_styles.css` file with the new CSS provided.
3. Ensure that your `config.py` and `report_template.html` files are up to date and in the correct locations.
4. Run the script as before.

These changes will result in a report with:
- A more visually appealing executive summary with severity breakdowns under each application name.
- Consistent color coding for priority levels throughout the entire report.
- Improved readability and visual hierarchy in the executive summary and detailed sections.

The report should now be more visually engaging and easier to scan for important information, with priority levels clearly indicated by color throughout the document.
