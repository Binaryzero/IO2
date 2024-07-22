import csv
from collections import Counter
from datetime import datetime
from config import COLUMN_SEVERITY_RISK, COLUMN_HOST_NAME, COLUMN_SOURCES, COLUMN_DUE_DATE, PRIORITY_LEVELS

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

def get_top_vulnerable_hosts(data, priority, top_n):
    priority_data = get_priority_data(data, priority)
    host_counter = Counter(get_host_or_source(row) for row in priority_data if not is_non_server_vuln(row))
    return host_counter.most_common(top_n)

def get_due_date_outlook(data, priority, time_frames):
    priority_data = get_priority_data(data, priority)
    today = datetime.now().date()
    due_dates = [parse_date(row[COLUMN_DUE_DATE]).date() for row in priority_data]
    
    past_due = sum(1 for date in due_dates if date < today)
    due_today = sum(1 for date in due_dates if date == today)
    
    due_within_periods = {days: sum(1 for date in due_dates if 0 <= (date - today).days <= days) for days in time_frames}
    
    total_vulnerabilities = len(priority_data)
    result = {
        'past_due': (past_due, past_due/total_vulnerabilities if total_vulnerabilities else 0),
        'due_today': (due_today, due_today/total_vulnerabilities if total_vulnerabilities else 0)
    }
    result.update({days: (count, count/total_vulnerabilities if total_vulnerabilities else 0) 
                   for days, count in due_within_periods.items()})
    
    return result

def process_rd_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Group data by Application
    grouped_data = {}
    owner_summary = {}
    
    for row in data:
        app = row['App']
        owner = row['AssignedToFullName']
        condition = row['Deliverable Condition']
        
        if app not in grouped_data:
            grouped_data[app] = {
                'AppID': row['AppID'],
                'Deliverables': []
            }
        grouped_data[app]['Deliverables'].append({
            'Owner': owner,
            'Condition': condition
        })
        
        # Update owner summary
        if owner not in owner_summary:
            owner_summary[owner] = {}
        if condition not in owner_summary[owner]:
            owner_summary[owner][condition] = 0
        owner_summary[owner][condition] += 1
    
    return grouped_data, owner_summary
