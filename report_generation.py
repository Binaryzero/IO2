from collections import Counter
from datetime import datetime
from config import *
from data_processing import get_host_or_source, is_non_server_vuln, get_top_vulnerable_hosts, get_due_date_outlook, parse_date

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

def generate_app_deliverables_html(rd_data, owner_summary):
    html = "<h2>Application Deliverables</h2>"
    for app, app_data in rd_data.items():
        html += f"<h3>{app} (ID: {app_data['AppID']})</h3>"
        html += "<table>"
        html += "<tr><th>Owner</th><th>Condition</th></tr>"
        for deliverable in app_data['Deliverables']:
            condition_class = ''
            if 'Past Due' in deliverable['Condition']:
                condition_class = 'class="priority-high"'
            elif 'Due 0 to 10 Days' in deliverable['Condition']:
                condition_class = 'class="priority-medium"'
            html += f"<tr><td>{deliverable['Owner']}</td><td {condition_class}>{deliverable['Condition']}</td></tr>"
        html += "</table>"
    
    html += "<h2>Owner Summary</h2>"
    html += "<table>"
    html += "<tr><th>Owner</th><th>Condition</th><th>Count</th></tr>"
    for owner, conditions in owner_summary.items():
        for condition, count in conditions.items():
            condition_class = ''
            if 'Past Due' in condition:
                condition_class = 'class="priority-high"'
            elif 'Due 0 to 10 Days' in condition:
                condition_class = 'class="priority-medium"'
            html += f"<tr><td>{owner}</td><td {condition_class}>{condition}</td><td>{count}</td></tr>"
    html += "</table>"
    
    return html

def generate_html_report(data, rd_data, owner_summary):
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
        top_hosts = get_top_vulnerable_hosts(data, priority, TOP_SERVERS_COUNT)
        vulnerable_hosts_by_priority += f'<h4 class="{class_name}">{priority}</h4>'
        if top_hosts:
            vulnerable_hosts_by_priority += generate_html_list(top_hosts)
        else:
            vulnerable_hosts_by_priority += "<p>No vulnerabilities found for this priority.</p>"
        
        due_date_outlook = get_due_date_outlook(data, priority, DUE_DATE_TIME_FRAMES)
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
    
    app_deliverables_html = generate_app_deliverables_html(rd_data, owner_summary)
    
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
        vulnerabilities_by_app=vulnerabilities_by_app,
        app_deliverables=app_deliverables_html
    )
