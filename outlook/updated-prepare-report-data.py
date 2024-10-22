def prepare_report_data(data: List[Dict[str, str]], rd_data: Dict[str, Dict[str, List[Dict[str, str]]]], owner_summary: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    Prepare the data for the Jinja2 template.

    Args:
        data (List[Dict[str, str]]): List of vulnerability data dictionaries.
        rd_data (Dict[str, Dict[str, List[Dict[str, str]]]]): Processed application deliverables data.
        owner_summary (Dict[str, Dict[str, int]]): Summary of deliverables by owner.

    Returns:
        Dict[str, Any]: A dictionary containing all the data needed for the report template.
    """
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    vulnerability_counter = Counter(row[COLUMN_TITLE] for row in data)
    most_common_vulnerabilities = vulnerability_counter.most_common(TOP_VULNERABILITIES_COUNT)
    
    vulnerable_hosts_by_priority = {
        priority: get_top_vulnerable_hosts(data, priority, TOP_SERVERS_COUNT)
        for priority in PRIORITY_LEVELS
    }
    
    due_dates_by_priority = {
        priority: get_due_date_outlook(data, priority, DUE_DATE_TIME_FRAMES)
        for priority in PRIORITY_LEVELS
    }
    
    app_id_count = Counter(row[COLUMN_APPLICATION_ID] for row in data)
    vulnerabilities_by_app = []
    for app_id, count in app_id_count.most_common():
        app_name = next((row[COLUMN_APPLICATION_FULL_NAME] for row in data if row[COLUMN_APPLICATION_ID] == app_id), "Unknown")
        app_data = [row for row in data if row[COLUMN_APPLICATION_ID] == app_id]
        app_priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in app_data)
        vulnerabilities_by_app.append({
            'name': app_name,
            'id': app_id,
            'total': count,
            'priorities': {priority: app_priority_count[priority] for priority in PRIORITY_LEVELS}
        })
    
    # Generate executive summary (you may need to implement this function)
    executive_summary = generate_executive_summary(data, owner_summary)
    
    return {
        'executive_summary': executive_summary,
        'total_vulnerabilities': total_vulnerabilities,
        'unique_vulnerabilities': unique_vulnerabilities,
        'affected_hosts': affected_hosts,
        'priority_breakdown': [(priority, priority_count[priority], priority_count[priority]/total_vulnerabilities) for priority in PRIORITY_LEVELS],
        'most_common_vulnerabilities': most_common_vulnerabilities,
        'vulnerable_hosts_by_priority': vulnerable_hosts_by_priority,
        'due_dates_by_priority': due_dates_by_priority,
        'vulnerabilities_by_app': vulnerabilities_by_app,
        'owner_deliverables': owner_summary
    }
