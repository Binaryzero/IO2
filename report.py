import csv
from collections import Counter
from datetime import datetime, timedelta
import pyperclip 

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

def generate_html_report(data):
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

        <h2>Overview</h2>
        <p>This report summarizes the security vulnerabilities detected across our server infrastructure. The data covers {total_vulnerabilities} unique vulnerability instances affecting {affected_servers} servers.</p>

        <h2>Key Statistics</h2>
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

        <h2>Most Common Vulnerabilities</h2>
        {generate_html_list(most_common_vulnerabilities)}

        <h2>Servers with Most Vulnerabilities (by Priority)</h2>
    """

    for priority in range(1, 4):
        top_servers = get_top_vulnerable_servers(data, priority)
        html += f"<h3>Priority {priority}</h3>"
        if top_servers:
            html += generate_html_list(top_servers)
        else:
            html += "<p>No vulnerabilities found for this priority.</p>"

    html += "<h2>Upcoming Due Dates (by Priority)</h2>"

    for priority in range(1, 4):
        due_date_outlook = get_due_date_outlook(data, priority)
        html += f"<h3>Priority {priority}</h3>"
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            html += "<table><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>"
            for days, (count, percentage) in due_date_outlook.items():
                html += f"<tr><td>{days}-day outlook</td><td>{count}</td><td>{percentage:.1%}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No vulnerabilities found for this priority.</p>"

    html += """
        <h2>Recommendations</h2>
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

def copy_to_clipboard(html):
    pyperclip.copy(html)
    print("HTML report copied to clipboard. You can now paste it directly into an Outlook email.")

if __name__ == "__main__":
    data = read_csv_data('expanded_data.csv')
    report = generate_html_report(data)
    
    # Write to file
    with open('security_report.html', 'w') as f:
        f.write(report)
    
    # Copy to clipboard
    copy_to_clipboard(report)
    
    print("Report generated successfully!")