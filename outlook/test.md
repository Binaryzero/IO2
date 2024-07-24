Certainly! I'll provide you with a complete `report_generation.py` script that incorporates all the changes and improvements we've discussed. This script will include detailed logging and error handling to help identify any issues in the report generation process.

```python
"""
report_generation.py

This module is responsible for generating the HTML report based on the processed vulnerability data.
It uses Jinja2 for templating to create a more flexible and maintainable report.
"""

import logging
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
from config import (
    HTML_TEMPLATE_PATH,
    CSS_STYLE_PATH,
    PRIORITY_LEVELS,
    TOP_VULNERABILITIES_COUNT,
    TOP_SERVERS_COUNT,
    DUE_DATE_TIME_FRAMES,
    COLUMN_TITLE,
    COLUMN_SEVERITY_RISK,
    COLUMN_APPLICATION_ID,
    COLUMN_APPLICATION_FULL_NAME,
    COLUMN_DUE_DATE,
    COLUMN_HOST_NAME,
    COLUMN_SOURCES
)
from data_processing import (
    get_host_or_source,
    is_non_server_vuln,
    get_top_vulnerable_hosts,
    get_due_date_outlook,
    parse_date
)

def get_condition_class(condition: str) -> str:
    """
    Determine the CSS class for a given condition.

    Args:
        condition (str): The condition string.

    Returns:
        str: The corresponding CSS class.
    """
    if 'Past Due with No Plan' in condition:
        return 'priority-critical'
    elif 'Past Due with Plan' in condition:
        return 'priority-high'
    elif 'Due 0 to 10 Days' in condition:
        return 'priority-medium'
    else:
        return ''

def generate_executive_summary(data: List[Dict[str, str]], owner_summary: Dict[str, Dict[str, int]]) -> str:
    """
    Generate the executive summary for the security vulnerability report.

    Args:
        data (List[Dict[str, str]]): List of vulnerability data dictionaries.
        owner_summary (Dict[str, Dict[str, int]]): Summary of deliverables by owner.

    Returns:
        str: HTML string containing the executive summary.
    """
    logging.info("Generating executive summary")
    total_vulnerabilities = len(data)
    unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
    affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
    priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
    
    today = datetime.now().date()
    past_due_vulnerabilities = sum(1 for row in data if parse_date(row[COLUMN_DUE_DATE]).date() < today)

    total_deliverables = sum(sum(conditions.values()) for conditions in owner_summary.values())
    past_due_deliverables = sum(sum(count for cond, count in conditions.items() if 'Past Due' in cond) for conditions in owner_summary.values())
    
    summary = f"""
    <h2>Executive Summary</h2>
    
    <p>This report provides an overview of the current security vulnerability landscape within our organization. 
    Key findings from the analysis are as follows:</p>
    
    <ul>
        <li>Total identified vulnerabilities: <strong>{total_vulnerabilities}</strong></li>
        <li>Unique vulnerabilities: <strong>{unique_vulnerabilities}</strong></li>
        <li>Affected hosts/servers: <strong>{affected_hosts}</strong></li>
        <li>Past due vulnerabilities: <strong class="priority-high">{past_due_vulnerabilities}</strong></li>
    </ul>
    
    <h3>Priority Breakdown:</h3>
    <ul>
    """
    
    for priority in PRIORITY_LEVELS:
        count = priority_count[priority]
        percentage = count / total_vulnerabilities * 100 if total_vulnerabilities > 0 else 0
        priority_class = priority.lower().replace(' ', '-')
        summary += f'<li class="{priority_class}">{priority}: <strong>{count}</strong> ({percentage:.1f}%)</li>'
    
    summary += f"""
    </ul>
    
    <h3>Deliverable Summary:</h3>
    <p>There are <strong>{total_deliverables}</strong> total deliverables across all owners.</p>
    <p><strong class="priority-high">Past Due Deliverables: {past_due_deliverables}</strong></p>
    
    <h4>Critical Deliverables:</h4>
    <table class="summary-table">
    <tr><th>Owner</th><th>Condition</th><th>Count</th></tr>
    """
    
    for owner, conditions in owner_summary.items():
        critical_conditions = {cond: count for cond, count in conditions.items() if 'Past Due' in cond or 'Due 0 to 10 Days' in cond}
        if critical_conditions:
            for cond, count in critical_conditions.items():
                condition_class = get_condition_class(cond)
                summary += f"<tr><td>{owner}</td><td class='{condition_class}'>{cond}</td><td>{count}</td></tr>"
    
    summary += """
    </table>
    
    <p>Immediate action is required to address past due and high-priority vulnerabilities and deliverables. 
    Please refer to the detailed sections below for specific information on vulnerable hosts, 
    upcoming due dates, and application-specific vulnerabilities.</p>
    """
    
    logging.info("Executive summary generated")
    return summary

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
    logging.info("Preparing report data")
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
    
    executive_summary = generate_executive_summary(data, owner_summary)
    
    report_data = {
        'executive_summary': executive_summary,
        'total_vulnerabilities': total_vulnerabilities,
        'unique_vulnerabilities': unique_vulnerabilities,
        'affected_hosts': affected_hosts,
        'priority_breakdown': [(priority, priority_count[priority], priority_count[priority]/total_vulnerabilities if total_vulnerabilities > 0 else 0) for priority in PRIORITY_LEVELS],
        'most_common_vulnerabilities': most_common_vulnerabilities,
        'vulnerable_hosts_by_priority': vulnerable_hosts_by_priority,
        'due_dates_by_priority': due_dates_by_priority,
        'vulnerabilities_by_app': vulnerabilities_by_app,
        'owner_deliverables': owner_summary
    }
    
    logging.info("Prepared report data with the following keys:")
    for key, value in report_data.items():
        logging.info(f"  - {key}: {type(value)}")
        if isinstance(value, (list, dict)):
            logging.info(f"    Length: {len(value)}")
    
    return report_data

def generate_html_report(data: List[Dict[str, str]], rd_data: Dict[str, Dict[str, List[Dict[str, str]]]], owner_summary: Dict[str, Dict[str, int]]) -> str:
    """
    Generate the complete HTML report using Jinja2 templating.

    Args:
        data (List[Dict[str, str]]): List of vulnerability data dictionaries.
        rd_data (Dict[str, Dict[str, List[Dict[str, str]]]]): Processed application deliverables data.
        owner_summary (Dict[str, Dict[str, int]]): Summary of deliverables by owner.

    Returns:
        str: Complete HTML report as a string.
    """
    logging.info("Starting generate_html_report function")
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"Current directory: {current_dir}")
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(current_dir))
    logging.info("Jinja2 Environment set up")
    
    # Verify template file exists
    template_path = os.path.join(current_dir, HTML_TEMPLATE_PATH)
    if not os.path.exists(template_path):
        logging.error(f"Template file not found: {template_path}")
        raise FileNotFoundError(f"Template file not found: {template_path}")
    logging.info(f"Template file found: {template_path}")
    
    # Load the template
    try:
        template = env.get_template(HTML_TEMPLATE_PATH)
        logging.info("Template loaded successfully")
    except Exception as e:
        logging.error(f"Error loading template: {str(e)}")
        raise
    
    # Read CSS styles
    try:
        with open(CSS_STYLE_PATH, 'r', encoding='utf-8') as f:
            styles = f.read()
        logging.info(f"CSS styles loaded from {CSS_STYLE_PATH}")
    except Exception as e:
        logging.error(f"Error reading CSS file: {str(e)}")
        styles = ""  # Use empty styles if file can't be read
    
    # Prepare data for the template
    report_data = prepare_report_data(data, rd_data, owner_summary)
    logging.info("Report data prepared")
    
    # Render the template
    try:
        rendered_html = template.render(styles=styles, get_condition_class=get_condition_class, **report_data)
        logging.info("Template rendered successfully")
        logging.info(f"Length of rendered HTML: {len(rendered_html)}")
        logging.info(f"First 200 characters of rendered HTML: {rendered_html[:200]}")
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        raise
    
    return rendered_html

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Add any testing or debugging code here
    logging.info("Running report_generation.py directly")
    
    # You can add test data and call functions here for debugging
    # For example:
    # test_data = [...]  # Add some test data
    # test_rd_data = {...}  # Add some test rd_data
    # test_owner_summary = {...}  # Add some test owner_summary
    # test_report = generate_html_report(test_data, test_rd_data, test_owner_summary)
    # print(test_report[:1000])  # Print the first 1000 characters of the test report

```

This script includes:

1. Detailed logging throughout the process.
2. Error handling for file operations and template rendering.
3. A complete implementation of `generate_executive_summary`, `prepare_report_data`, and `generate_html_report` functions.
4. Type hints for better code readability and maintainability.
5. A section at the end for running tests or debugging when the script is run directly.

To use this script:

1. Ensure that all the imported modules and config variables are correctly set up in your project.
2. Make sure the Jinja2 template file (HTML_TEMPLATE_PATH) and CSS file (CSS_STYLE_PATH) exist in the correct locations.
3. Call the `generate_html_report` function from your main script, passing in the necessary data.

If you're still experiencing issues with the report generation, you can run this script directly (python report_generation.py) after adding some test data at the bottom. This will help isolate any problems specific to the report generation process.

Let me know if you need any clarification on any part of this script or if you're still encountering issues when generating the report.
