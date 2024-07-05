Certainly! I'll update the CSS to include more color and improve the overall visual appeal of the report. Here's an enhanced version of the CSS with more color and some additional styling:



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

```

Now, let's update the HTML template to incorporate these new styles:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Summary Report</title>
    <style>
        {styles}
    </style>
</head>
<body>
    <h1>Security Vulnerability Summary Report</h1>

    <div class="executive-summary">
        {executive_summary}
    </div>

    <hr>

    <h2>Detailed Report</h2>

    <div class="stat-box">
        <h3>Key Statistics</h3>
        <ul>
            <li>Total vulnerabilities: {total_vulnerabilities}</li>
            <li>Unique vulnerabilities: {unique_vulnerabilities}</li>
            <li>Affected host names: {affected_servers}</li>
            <li>Priority breakdown:
                <ul>
                    <li class="priority-high">Priority 1 (High): {priority_1_count} ({priority_1_percentage:.1%})</li>
                    <li class="priority-medium">Priority 2 (Medium): {priority_2_count} ({priority_2_percentage:.1%})</li>
                    <li class="priority-low">Priority 3 (Low): {priority_3_count} ({priority_3_percentage:.1%})</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="stat-box">
        <h3>Most Common Vulnerabilities</h3>
        {most_common_vulnerabilities}
    </div>

    <div class="stat-box">
        <h3>Host Names with Most Vulnerabilities (by Priority)</h3>
        {vulnerable_servers_by_priority}
    </div>

    <div class="stat-box">
        <h3>Upcoming Due Dates (by Priority)</h3>
        {due_dates_by_priority}
    </div>

    <div class="stat-box">
        <h3>Vulnerabilities by Application ID</h3>
        {vulnerabilities_by_app_id}
    </div>

    <p>This summary provides a high-level overview of the current security posture. For detailed information on specific vulnerabilities or affected host names, please refer to the full vulnerability report.</p>
</body>
</html>

```

To implement these changes:

1. Replace the content of your `report_styles.css` file with the CSS provided above.
2. Update your `report_template.html` file with the new HTML template provided.
3. Make sure the path to these files in your `config.py` is correct.

These changes will give your report a more colorful and professional appearance:

- A light blue background for the entire report
- Colored headings to differentiate sections
- A highlighted executive summary section
- Color-coded priority levels
- Boxed sections for better visual separation of information
- Improved table styling with alternating row colors
- Subtle shadows and borders to add depth

The new design should make the report more visually appealing and easier to read, while still maintaining a professional look suitable for a security vulnerability report.
