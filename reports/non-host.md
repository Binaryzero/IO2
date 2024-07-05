I apologize for the oversight. It seems the 'past_due' key is not being properly added to the due date outlook dictionary. Let's fix this issue by modifying the `get_due_date_outlook` function. Here's the corrected version:



```python
def get_due_date_outlook(data, priority):
    priority_data = get_priority_data(data, priority)
    today = datetime.now().date()
    due_dates = [parse_date(row[COLUMN_DUE_DATE]).date() for row in priority_data]
    
    past_due = sum(1 for date in due_dates if date < today)
    due_today = sum(1 for date in due_dates if date == today)
    
    due_within_periods = {days: sum(1 for date in due_dates if 0 <= (date - today).days <= days) for days in DUE_DATE_TIME_FRAMES}
    
    total_vulnerabilities = len(priority_data)
    result = {
        'past_due': (past_due, past_due/total_vulnerabilities if total_vulnerabilities else 0),
        'due_today': (due_today, due_today/total_vulnerabilities if total_vulnerabilities else 0)
    }
    result.update({days: (count, count/total_vulnerabilities if total_vulnerabilities else 0) 
                   for days, count in due_within_periods.items()})
    
    return result

```

Now, let's update the part of the `generate_html_report` function that uses this data to ensure it handles cases where 'past_due' or 'due_today' might not be present:



```python
def generate_html_report(data):
    # ... [previous parts of the function remain the same] ...

    due_dates_by_priority = ""
    for priority, class_name in zip(PRIORITY_LEVELS, ['priority-high', 'priority-medium', 'priority-low']):
        due_date_outlook = get_due_date_outlook(data, priority)
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

    # ... [rest of the function remains the same] ...

```

These changes should resolve the KeyError you're encountering. The `get_due_date_outlook` function now explicitly adds 'past_due' and 'due_today' keys to the result dictionary, and the report generation checks if these keys exist before trying to use them.

To implement these changes:

1. Replace the `get_due_date_outlook` function in your script with the corrected version provided above.
2. Update the `generate_html_report` function, specifically the part that generates the due dates section, with the new code provided.
3. Keep all other parts of your script the same.
4. Run the script again.

These modifications should eliminate the KeyError and ensure that the past due and due today information is correctly included in your report. If you encounter any other issues, please let me know, and I'll be happy to help further.
