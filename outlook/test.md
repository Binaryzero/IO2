I apologize for the confusion. Now that I can see your template, I can identify the issues causing the error. There are several problems with the template structure that need to be addressed. Let's fix them:

```html
{% raw %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Summary Report</title>
    <style>
        {{ styles | safe }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Vulnerability Summary Report</h1>

        {{ executive_summary | safe }}

        <div class="stat-box">
            <h2>Key Statistics</h2>
            <ul>
                <li>Total vulnerabilities: {{ total_vulnerabilities }}</li>
                <li>Unique vulnerabilities: {{ unique_vulnerabilities }}</li>
                <li>Affected host names: {{ affected_hosts }}</li>
                <li>Priority breakdown:
                    <ul>
                    {% for priority, count, percentage in priority_breakdown %}
                        <li class="{{ priority | lower | replace(' ', '-') }}">
                            {{ priority }}: {{ count }} ({{ '{:.1%}'.format(percentage) }})
                        </li>
                    {% endfor %}
                    </ul>
                </li>
            </ul>
        </div>

        <div class="stat-box">
            <h2>Most Common Vulnerabilities</h2>
            <ol>
            {% for vulnerability, count in most_common_vulnerabilities %}
                <li>{{ vulnerability }}: {{ count }} instances</li>
            {% endfor %}
            </ol>
        </div>

        <div class="stat-box">
            <h2>Host Names with Most Vulnerabilities (by Priority)</h2>
            {% for priority, hosts in vulnerable_hosts_by_priority.items() %}
                <h3 class="{{ priority | lower | replace(' ', '-') }}">{{ priority }}</h3>
                {% if hosts %}
                    <ol>
                    {% for host, count in hosts %}
                        <li>{{ host }}: {{ count }} instances</li>
                    {% endfor %}
                    </ol>
                {% else %}
                    <p>No vulnerabilities found for this priority.</p>
                {% endif %}
            {% endfor %}
        </div>

        <div class="stat-box">
            <h2>Upcoming Due Dates (by Priority)</h2>
            {% for priority, outlook in due_dates_by_priority.items() %}
                <h3 class="{{ priority | lower | replace(' ', '-') }}">{{ priority }}</h3>
                {% if outlook %}
                    <table class="summary-table">
                        <tr>
                            <th>Outlook</th>
                            <th>Vulnerabilities</th>
                            <th>Percentage</th>
                        </tr>
                        {% for period, (count, percentage) in outlook.items() %}
                        <tr>
                            <td>{{ period }}</td>
                            <td>{{ count }}</td>
                            <td>{{ '{:.1%}'.format(percentage) }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                {% else %}
                    <p>No vulnerabilities found for this priority.</p>
                {% endif %}
            {% endfor %}
        </div>

        <div class="stat-box">
            <h2>Vulnerabilities by Application</h2>
            {% for app in vulnerabilities_by_app %}
                <h3>{{ app.name }} (ID: {{ app.id }})</h3>
                <p>Total vulnerabilities: {{ app.total }}</p>
                <ul>
                {% for priority, count in app.priorities.items() %}
                    <li class="{{ priority | lower | replace(' ', '-') }}">{{ priority }}: {{ count }}</li>
                {% endfor %}
                </ul>
            {% endfor %}
        </div>

        <div class="stat-box">
            <h2>Owner Deliverables Summary</h2>
            <table class="summary-table">
                <tr>
                    <th>Owner</th>
                    <th>Conditions</th>
                </tr>
                {% for owner, conditions in owner_deliverables.items() %}
                <tr>
                    <td>{{ owner }}</td>
                    <td>
                        {% for condition, count in conditions.items() %}
                        <div class="{{ get_condition_class(condition) }}">
                            {{ condition }}: {{ count }}
                        </div>
                        {% endfor %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <footer>
            <p>This report was generated automatically. If you have any questions or concerns, please contact the security team.</p>
        </footer>
    </div>
</body>
</html>
{% endraw %}

```

Key changes made:

1. Added proper HTML structure with `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` tags.
2. Removed the custom `:::` syntax, which is not part of Jinja2, and replaced it with proper HTML `<div>` elements.
3. Fixed the loops and conditionals to properly close with `{% endfor %}` and `{% endif %}`.
4. Corrected the syntax for applying classes, changing `.{{ ... }}` to `class="{{ ... }}"`.
5. Structured the tables properly with `<table>`, `<tr>`, and `<td>` tags.
6. Ensured all sections are properly nested and closed.

Please replace your current template file (`complete-jinja2-report-template.html`) with this corrected version. After making this change, try running your report generation script again. The "unexpected end of template" error should be resolved, and you should get a properly rendered HTML report.

If you encounter any other issues or if parts of the report are still not rendering correctly, please let me know, and I'll be happy to help you further.
