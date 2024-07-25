Certainly! Adding the priority to the Exceptions and Acceptable Use items will provide more detailed information in the report. We'll need to modify several functions to include this information. Let's update the relevant parts of the code.



```python
from collections import Counter, defaultdict
from datetime import datetime
from config import *
from data_processing import get_host_or_source, is_non_server_vuln, get_top_vulnerable_hosts, get_due_date_outlook, parse_date

# ... (previous functions remain the same)

def generate_vulnerability_summary(data):
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    today = datetime.now().date()
    past_due_vulnerabilities = sum(1 for row in data 
                                   if parse_date(row[COLUMN_DUE_DATE]).date() < today 
                                   and row[COLUMN_ERP_SCORECARD_STATUS] not in [ERP_EXCEPTION, ERP_ACCEPTABLE_USE])
    
    exceptions = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                         for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
    acceptable_use = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                             for row in data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)

    summary = f"""
    <h3>Vulnerability Summary:</h3>
    <p>This report covers {total_vulnerabilities} total vulnerabilities, including {unique_vulnerabilities} unique vulnerabilities across {affected_hosts} hosts/sources.</p>
    <p><strong class="priority-high">Past Due Vulnerabilities: {past_due_vulnerabilities}</strong></p>
    
    <h4>Exceptions and Acceptable Use by Priority:</h4>
    <table class="summary-table">
    <tr><th>Priority</th><th>Exceptions</th><th>Acceptable Use</th></tr>
    """
    
    for priority in PRIORITY_LEVELS:
        exception_count = exceptions[(priority, ERP_EXCEPTION)]
        acceptable_use_count = acceptable_use[(priority, ERP_ACCEPTABLE_USE)]
        class_name = 'priority-high' if priority == PRIORITY_LEVELS[0] else ('priority-medium' if priority == PRIORITY_LEVELS[1] else 'priority-low')
        summary += f'<tr class="{class_name}"><td>{priority}</td><td>{exception_count}</td><td>{acceptable_use_count}</td></tr>'
    
    summary += f"""
    </table>
    <p><strong class="priority-medium">Total Exceptions: {sum(exceptions.values())}</strong></p>
    <p><strong class="priority-low">Total Acceptable Use: {sum(acceptable_use.values())}</strong></p>
    
    <h4>Vulnerabilities by Priority:</h4>
    <table class="summary-table">
    <tr><th>Priority</th><th>Count</th><th>Percentage</th></tr>
    """
    
    for priority in PRIORITY_LEVELS:
        count = priority_count[priority]
        class_name = 'priority-high' if priority == PRIORITY_LEVELS[0] else ('priority-medium' if priority == PRIORITY_LEVELS[1] else 'priority-low')
        summary += f'<tr class="{class_name}"><td>{priority}</td><td>{count}</td><td>{count/total_vulnerabilities:.1%}</td></tr>'
    
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
        
        app_exceptions = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                                 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
        app_acceptable_use = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                                     for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
        
        exceptions_breakdown = " | ".join(f'<span class="{class_name}">{priority}: {app_exceptions[(priority, ERP_EXCEPTION)]}</span>' 
                                          for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']))
        acceptable_use_breakdown = " | ".join(f'<span class="{class_name}">{priority}: {app_acceptable_use[(priority, ERP_ACCEPTABLE_USE)]}</span>' 
                                              for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']))
        
        summary += f"""<tr>
            <td>{app_name} (ID: {app_id})</td>
            <td>{count}</td>
            <td>{priority_breakdown}</td>
            <td>{exceptions_breakdown}</td>
            <td>{acceptable_use_breakdown}</td>
        </tr>"""
    
    summary += "</table>"
    return summary

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
        app_exceptions = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                                 for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_EXCEPTION)
        app_acceptable_use = Counter((row[COLUMN_SEVERITY_RISK], row[COLUMN_ERP_SCORECARD_STATUS]) 
                                     for row in app_data if row[COLUMN_ERP_SCORECARD_STATUS] == ERP_ACCEPTABLE_USE)
        vulnerabilities_by_app += "<ul>"
        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
            vulnerabilities_by_app += f'<li class="{class_name}">{priority}: {app_priority_count[priority]}</li>'
        vulnerabilities_by_app += "</ul>"
        vulnerabilities_by_app += "<h5>Exceptions:</h5><ul>"
        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
            vulnerabilities_by_app += f'<li class="{class_name}">{priority}: {app_exceptions[(priority, ERP_EXCEPTION)]}</li>'
        vulnerabilities_by_app += "</ul>"
        vulnerabilities_by_app += "<h5>Acceptable Use:</h5><ul>"
        for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
            vulnerabilities_by_app += f'<li class="{class_name}">{priority}: {app_acceptable_use[(priority, ERP_ACCEPTABLE_USE)]}</li>'
        vulnerabilities_by_app += "</ul>"
    return vulnerabilities_by_app

# ... (rest of the code remains the same)

# The report generation has been updated to include priority information for Exceptions and Acceptable Use items.
# Key changes:
# 1. In the vulnerability summary, we now show Exceptions and Acceptable Use counts by priority.
# 2. In the top applications summary, we've added detailed breakdowns of Exceptions and Acceptable Use by priority for each application.
# 3. In the vulnerabilities by app section, we now show Exceptions and Acceptable Use counts by priority for each application.
#
# These changes provide more granular information about the nature of exceptions and acceptable use cases,
# allowing for better understanding and decision-making based on the severity of the vulnerabilities involved.

```

This updated version of the report generation code now includes priority information for Exceptions and Acceptable Use items throughout the report. Here's a summary of the key changes:

1. In the `generate_vulnerability_summary` function:
   - We now use a Counter to track Exceptions and Acceptable Use cases by priority.
   - A new table is added to show Exceptions and Acceptable Use counts for each priority level.

2. In the `generate_top_applications_summary` function:
   - The table now includes detailed breakdowns of Exceptions and Acceptable Use by priority for each application.

3. In the `generate_vulnerabilities_by_app` function:
   - We've added separate sections for Exceptions and Acceptable Use, showing counts by priority for each application.

These changes provide more detailed information about the nature of exceptions and acceptable use cases, allowing for better understanding and decision-making based on the severity of the vulnerabilities involved.

The `generate_due_dates_summary` function was left unchanged as it already provided information by priority. However, if you want to add more detail to this section as well, we could modify it to show a breakdown of exceptions and acceptable use cases for each time frame.

Is there anything specific you'd like to modify or add to this updated report structure?
