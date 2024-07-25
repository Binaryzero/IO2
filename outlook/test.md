Certainly! Let's modify the code to allow the user to choose whether they want to generate a report for vulnerabilities, deliverables, or both. We'll update the `generate_html_report` function and add a new parameter to control this behavior. We'll also need to modify the `main.py` file to accommodate this new option.

First, let's update the `report_generation.py` file:



```python
# ... (previous imports and functions remain the same)

def generate_html_report(data, rd_data, owner_summary, report_type='both'):
    with open(HTML_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    with open(CSS_STYLE_PATH, 'r') as f:
        styles = f.read()
    
    executive_summary = ""
    vulnerability_details = ""
    deliverable_details = ""

    if report_type in ['vulnerabilities', 'both']:
        total_vulnerabilities = len(data)
        unique_vulnerabilities = len(set((row[COLUMN_TITLE], row[COLUMN_SEVERITY_RISK]) for row in data))
        affected_hosts = len(set(get_host_or_source(row) for row in data if not is_non_server_vuln(row)))
        priority_count = Counter(row[COLUMN_SEVERITY_RISK] for row in data)
        
        vulnerability_counter = Counter(row[COLUMN_TITLE] for row in data)
        most_common_vulnerabilities = generate_html_list(vulnerability_counter.most_common(TOP_VULNERABILITIES_COUNT))
        
        vulnerable_hosts_by_priority = generate_vulnerable_hosts_summary(data)
        due_dates_by_priority = generate_due_dates_summary(data)
        vulnerabilities_by_app = generate_vulnerabilities_by_app(data)

        executive_summary += generate_vulnerability_summary(data)
        executive_summary += generate_top_applications_summary(data)

        vulnerability_details = f"""
        <h2>Vulnerability Details</h2>
        <h3>Most Common Vulnerabilities</h3>
        {most_common_vulnerabilities}
        <h3>Vulnerable Hosts by Priority</h3>
        {vulnerable_hosts_by_priority}
        <h3>Due Dates by Priority</h3>
        {due_dates_by_priority}
        <h3>Vulnerabilities by Application</h3>
        {vulnerabilities_by_app}
        """

    if report_type in ['deliverables', 'both']:
        executive_summary = generate_deliverable_summary(owner_summary) + executive_summary
        deliverable_details = generate_owner_deliverables_html(owner_summary)

    if report_type == 'both':
        report_title = "Security Vulnerability and Deliverable Summary Report"
    elif report_type == 'vulnerabilities':
        report_title = "Security Vulnerability Summary Report"
    else:
        report_title = "Security Deliverable Summary Report"

    return template.format(
        styles=styles,
        report_title=report_title,
        executive_summary=executive_summary,
        vulnerability_details=vulnerability_details,
        deliverable_details=deliverable_details
    )

# The report generation now includes an option to generate reports for vulnerabilities, deliverables, or both.
# Key changes:
# 1. Added a 'report_type' parameter to control what type of report to generate.
# 2. Conditional generation of report sections based on the report_type.
# 3. Dynamic report title based on the report_type.
# 4. Separate sections for vulnerability details and deliverable details.
#
# To use this new functionality, update the main.py file to pass the desired report_type to generate_html_report.

```

Now, let's update the `main.py` file to accommodate this new option:



```python
import argparse
from config import *
from data_processing import read_csv_data, process_rd_csv
from report_generation import generate_html_report
from email_sender import send_outlook_email

def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Generate and send security report.")
    parser.add_argument('--report-type', choices=['vulnerabilities', 'deliverables', 'both'], 
                        default='both', help="Type of report to generate")
    args = parser.parse_args()

    # Read vulnerability data
    vulnerability_data = read_csv_data(CSV_FILE_PATH)
    
    # Read and process application deliverables data
    rd_data, owner_summary = process_rd_csv(RD_CSV_FILE_PATH)
    
    # Generate HTML report
    report_html = generate_html_report(vulnerability_data, rd_data, owner_summary, args.report_type)
    
    # Save report to file
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    # Send email
    try:
        send_outlook_email(EMAIL_SUBJECT, report_html, EMAIL_RECIPIENTS)
        print(f"{args.report_type.capitalize()} report sent successfully via Outlook!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        print(f"The {args.report_type} report has been saved as '{OUTPUT_REPORT_PATH}' in the current directory.")

    print("Process completed.")

if __name__ == "__main__":
    main()

# The main script has been updated to accept a command-line argument for the report type.
# Key changes:
# 1. Added argparse to handle command-line arguments.
# 2. New --report-type argument to specify which type of report to generate.
# 3. Pass the report_type to the generate_html_report function.
# 4. Updated print statements to reflect the chosen report type.
#
# To run the script for a specific report type, use:
# python main.py --report-type vulnerabilities
# python main.py --report-type deliverables
# python main.py --report-type both
# If no argument is provided, it defaults to 'both'.

```

These changes allow the user to choose which type of report they want to generate and send. Here's a summary of the modifications:

1. In `report_generation.py`:
   - Added a `report_type` parameter to `generate_html_report` function.
   - Conditionally generate different parts of the report based on the `report_type`.
   - Created separate sections for vulnerability details and deliverable details.
   - Dynamically set the report title based on the `report_type`.

2. In `main.py`:
   - Added command-line argument parsing using `argparse`.
   - Introduced a new `--report-type` argument to specify which report to generate.
   - Pass the `report_type` to the `generate_html_report` function.
   - Updated print statements to reflect the chosen report type.

To use this new functionality, you can run the script with the following commands:

- For vulnerabilities only: `python main.py --report-type vulnerabilities`
- For deliverables only: `python main.py --report-type deliverables`
- For both (default): `python main.py --report-type both` or simply `python main.py`

This implementation provides flexibility for users to generate different types of reports as needed, while still maintaining the option to generate a comprehensive report covering both vulnerabilities and deliverables.

Is there anything else you'd like me to modify or explain further?
