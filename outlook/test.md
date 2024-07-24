from collections import Counter, defaultdict
from datetime import datetime
from config import *
from data_processing import get_host_or_source, is_non_server_vuln, get_top_vulnerable_hosts, get_due_date_outlook, parse_date

def generate_deliverable_summary(owner_summary):
    total_deliverables = sum(sum(conditions.values()) for conditions in owner_summary.values())
    past_due_deliverables = sum(sum(count for cond, count in conditions.items() if 'Past Due' in cond) for conditions in owner_summary.values())
    
    summary = f"""
    <h3>Deliverable Summary:</h3>
    <p>There are {total_deliverables} total deliverables across all owners.</p>
    <p><strong class="priority-high">Past Due Deliverables: {past_due_deliverables}</strong></p>
    
    <h4>Owners with Past Due or Due in 0 to 10 Days deliverables:</h4>
    <table class="summary-table">
    <tr><th>Owner</th><th>Condition</th><th>Count</th></tr>
    """
    
    for owner, conditions in owner_summary.items():
        critical_conditions = {cond: count for cond, count in conditions.items() if 'Past Due' in cond or 'Due 0 to 10 Days' in cond}
        if critical_conditions:
            for cond, count in critical_conditions.items():
                condition_class = get_condition_class(cond)
                summary += f"<tr><td>{owner}</td><td class='{condition_class}'>{cond}</td><td>{count}</td></tr>"
    
    summary += "</table>"
    return summary

def generate_vulnerability_summary(data):
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    today = datetime.now().date()
    past_due_vulnerabilities = sum(1 for row in data 
                                   if parse_date(row[COLUMN_DUE_DATE]).date() < today 
                                   and row[COLUMN_ERP_SCORECARD_STATUS] not in [ERP_EXCEPTION, ERP_ACCEPTABLE_USE])
    
    exceptions = sum(1 for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
    acceptable_use = sum(1 for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)

    summary = f"""
    <h3>Vulnerability Summary:</h3>
    <p>This report covers {total_vulnerabilities} total vulnerabilities, including {unique_vulnerabilities} unique vulnerabilities across {affected_hosts} hosts/sources.</p>
    <p><strong class="priority-high">Past Due Vulnerabilities: {past_due_vulnerabilities}</strong></p>
    <p><strong class="priority-medium">Exceptions: {exceptions}</strong></p>
    <p><strong class="priority-low">Acceptable Use: {acceptable_use}</strong></p>
    
    <table class="summary-table">
    <tr><th>Priority</th><th>Count</th><th>Percentage</th><th>Exceptions</th><th>Acceptable Use</th></tr>
    """
    
    for priority in PRIORITY_LEVELS:
        count = priority_count[priority]
        priority_exceptions = sum(1 for row in data if row[COLUMN_SEVERITY_RISK] == priority and row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
        priority_acceptable_use = sum(1 for row in data if row[COLUMN_SEVERITY_RISK] == priority and row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
        class_name = 'priority-high' if priority == PRIORITY_LEVELS[0] else ('priority-medium' if priority == PRIORITY_LEVELS[1] else 'priority-low')
        summary += f'<tr class="{class_name}"><td>{priority}</td><td>{count}</td><td>{count/total_vulnerabilities:.1%}</td><td>{priority_exceptions}</td><td>{priority_acceptable_use}</td></tr>'
    
    summary += "</table>"
    return summary

def generate_top_applications_summary(data):
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    top_app_ids = app_id_count.most_common(TOP_APP_IDS_COUNT)
    
    summary = """
    <h4>Top Applications by vulnerability count:</h4>
    <table class="summary-table">
    <tr><th>Application</th><th>Vulnerability Count</th><th>Priority Breakdown</th><th>Exceptions</th><th>Acceptable Use</th></tr>
    """
    
    for app_id, count in top_app_ids:
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        priority_breakdown = " | ".join(f'<span class="{class_name}">{priority}: {app_priority_count[priority]}</span>' 
                                        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']))
        app_exceptions = sum(1 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
        app_acceptable_use = sum(1 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
        summary += f"""<tr>
            <td>{app_name} (ID: {app_id})</td>
            <td>{count}</td>
            <td>{priority_breakdown}</td>
            <td>{app_exceptions}</td>
            <td>{app_acceptable_use}</td>
        </tr>"""
    
    summary += "</table>"
    return summary

def generate_executive_summary(data, owner_summary):
    deliverable_summary = generate_deliverable_summary(owner_summary)
    vulnerability_summary = generate_vulnerability_summary(data)
    top_applications_summary = generate_top_applications_summary(data)
    
    exceptions = sum(1 for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
    acceptable_use = sum(1 for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
    
    summary = f"""
    <h2>Executive Summary</h2>
    
    {deliverable_summary}
    
    {vulnerability_summary}
    
    {top_applications_summary}
    
    <p>Immediate action is required to address past due and high-priority vulnerabilities and deliverables. Note that {exceptions} vulnerabilities have exceptions and {acceptable_use} are marked for acceptable use.</p>
    """
    
    return summary

def generate_html_list(items):
    return "<ol>" + "".join(f"<li>{item[0]}: {item[1]} instances</li>" for item in items) + "</ol>"

def get_condition_class(condition):
    if 'Past Due with No Plan' in condition:
        return 'priority-critical'
    elif 'Past Due with Plan' in condition:
        return 'priority-high'
    elif 'Due 0 to 10 Days' in condition:
        return 'priority-medium'
    else:
        return ''

def generate_owner_deliverables_html(owner_summary):
    html = "<h2>Owner Deliverables Summary</h2>"
    html += "<table class='summary-table'>"
    html += "<tr><th>Owner</th><th>Conditions</th></tr>"
    
    for owner, conditions in owner_summary.items():
        html += f"<tr><td>{owner}</td><td>"
        for condition, count in sorted(conditions.items(), key=lambda x: (x[1], x[0]), reverse=True):
            condition_class = get_condition_class(condition)
            html += f"<div class='{condition_class}'>{condition}: {count}</div>"
        html += "</td></tr>"
    
    html += "</table>"
    
    return html

def generate_vulnerable_hosts_summary(data):
    vulnerable_hosts_by_priority = ""
    for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
        top_hosts = get_top_vulnerable_hosts(data, priority, TOP_SERVERS_COUNT)
        vulnerable_hosts_by_priority += f'<h4 class="{class_name}">{priority}</h4>'
        if top_hosts:
            vulnerable_hosts_by_priority += generate_html_list(top_hosts)
        else:
            vulnerable_hosts_by_priority += "<p>No vulnerabilities found for this priority.</p>"
    return vulnerable_hosts_by_priority

def generate_due_dates_summary(data):
    due_dates_by_priority = ""
    for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
        due_date_outlook = get_due_date_outlook(data, priority, DUE_DATE_TIME_FRAMES)
        due_dates_by_priority += f'<h4 class="{class_name}">{priority}</h4>'
        if sum(count for count, _ in due_date_outlook.values()) > 0:
            due_dates_by_priority += '<table class="summary-table"><tr><th>Outlook</th><th>Vulnerabilities</th><th>Percentage</th></tr>'
            if 'past_due' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-high"><td>Past Due</td><td>{due_date_outlook["past_due"][0]}</td><td>{due_date_outlook["past_due"][1]:.1%}</td></tr>'
            if 'due_today' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-high"><td>Due Today</td><td>{due_date_outlook["due_today"][0]}</td><td>{due_date_outlook["due_today"][1]:.1%}</td></tr>'
            for days, (count, percentage) in due_date_outlook.items():
                if days in DUE_DATE_TIME_FRAMES:
                    due_dates_by_priority += f'<tr><td>Next {days} days</td><td>{count}</td><td>{percentage:.1%}</td></tr>'
            
            if 'exceptions' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-medium"><td>Exceptions</td><td>{due_date_outlook["exceptions"][0]}</td><td>{due_date_outlook["exceptions"][1]:.1%}</td></tr>'
            if 'acceptable_use' in due_date_outlook:
                due_dates_by_priority += f'<tr class="priority-low"><td>Acceptable Use</td><td>{due_date_outlook["acceptable_use"][0]}</td><td>{due_date_outlook["acceptable_use"][1]:.1%}</td></tr>'
            
            due_dates_by_priority += "</table>"
        else:
            due_dates_by_priority += "<p>No vulnerabilities found for this priority.</p>"
    return due_dates_by_priority

def generate_vulnerabilities_by_app(data):
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    vulnerabilities_by_app = ""
    for app_id, count in app_id_count.most_common():
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        vulnerabilities_by_app += f"<h4>{app_name} (ID: {app_id})</h4>"
        vulnerabilities_by_app += f"<p>Total vulnerabilities: {count}</p>"
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        app_exceptions = sum(1 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
        app_acceptable_use = sum(1 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
        vulnerabilities_by_app += "<ul>"
        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
            vulnerabilities_by_app += f'<li class="{class_name}">{priority}: {app_priority_count[priority]}</li>'
        vulnerabilities_by_app += f'<li class="priority-medium">Exceptions: {app_exceptions}</li>'
        vulnerabilities_by_app += f'<li class="priority-low">Acceptable Use: {app_acceptable_use}</li>'
        vulnerabilities_by_app += "</ul>"
    return vulnerabilities_by_app

def generate_html_report(data, rd_data, owner_summary):
    with open(HTML_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    with open(CSS_STYLE_PATH, 'r') as f:
        styles = f.read()
    
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    vulnerability_counter = Counter(row[COLUMN_TITLE] for row in data)
    most_common_vulnerabilities = generate_html_list(vulnerability_counter.most_common(TOP_VULNERABILITIES_COUNT))
    
    vulnerable_hosts_by_priority = generate_vulnerable_hosts_summary(data)
    due_dates_by_priority = generate_due_dates_summary(data)
    vulnerabilities_by_app = generate_vulnerabilities_by_app(data)
    owner_deliverables_html = generate_owner_deliverables_html(owner_summary)
    
    return template.format(
        styles=styles,
        executive_summary=generate_executive_summary(data, owner_summary),
        total_vulnerabilities=total_vulnerabilities,
        unique_vulnerabilities=unique_vulnerabilities,
        # ... (previous code remains the same)

def generate_html_report(data, rd_data, owner_summary):
    with open(HTML_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    with open(CSS_STYLE_PATH, 'r') as f:
        styles = f.read()
    
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    vulnerability_counter = Counter(row[COLUMN_TITLE] for row in data)
    most_common_vulnerabilities = generate_html_list(vulnerability_counter.most_common(TOP_VULNERABILITIES_COUNT))
    
    vulnerable_hosts_by_priority = generate_vulnerable_hosts_summary(data)
    due_dates_by_priority = generate_due_dates_summary(data)
    vulnerabilities_by_app = generate_vulnerabilities_by_app(data)
    owner_deliverables_html = generate_owner_deliverables_html(owner_summary)
    
    return template.format(
        styles=styles,
        executive_summary=generate_executive_summary(data, owner_summary),
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
        app_deliverables=owner_deliverables_html
    )
