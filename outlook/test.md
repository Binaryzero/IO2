Thank you for providing that error message. It seems there's an issue with the structure of your Jinja2 template. The error "unexpected end of template, looking for endfor or else" typically occurs when there's an unclosed `for` loop or `if` statement in the template.

Let's diagnose and fix this issue:

1. First, let's examine the template. Add the following code to your `generate_html_report` function to print out the entire template content:

```python
def generate_html_report(data: List[Dict[str, str]], rd_data: Dict[str, Dict[str, List[Dict[str, str]]]], owner_summary: Dict[str, Dict[str, int]]) -> str:
    # ... (previous code)

    # Load the template
    try:
        template = env.get_template(HTML_TEMPLATE_PATH)
        logging.info("Template loaded successfully")
        
        # Print the entire template content
        with open(os.path.join(current_dir, HTML_TEMPLATE_PATH), 'r', encoding='utf-8') as f:
            template_content = f.read()
        logging.info("Full template content:")
        logging.info(template_content)
        
    except Exception as e:
        logging.error(f"Error loading template: {str(e)}")
        raise

    # ... (rest of the function)

```

2. Run your script and look at the logged template content. Pay special attention to line 26 and the surrounding lines. Look for any `for` loops or `if` statements that might not be properly closed.

3. Here's an example of how to correctly structure a `for` loop in a Jinja2 template:

```html
{% raw %}
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
{% endraw %}

```

4. And here's an example of a correct `if` statement:

```html
{% raw %}
{% if condition %}
    <p>This is shown if the condition is true.</p>
{% else %}
    <p>This is shown if the condition is false.</p>
{% endif %}
{% endraw %}

```

5. Once you've identified the issue in your template, fix it by ensuring all `for` loops and `if` statements are properly closed.

6. If you're having trouble identifying the issue, please provide the section of the template around line 26 (perhaps lines 20-30), and I can help you spot and fix the problem.

7. After fixing the template, run your script again and see if the error is resolved.

8. If you're still having issues, we can add some error handling to help identify problematic sections of the template. Add this to your `generate_html_report` function:

```python
from jinja2 import TemplateSyntaxError

def generate_html_report(data: List[Dict[str, str]], rd_data: Dict[str, Dict[str, List[Dict[str, str]]]], owner_summary: Dict[str, Dict[str, int]]) -> str:
    # ... (previous code)

    try:
        rendered_html = template.render(styles=styles, get_condition_class=get_condition_class, **report_data)
    except TemplateSyntaxError as e:
        logging.error(f"Template syntax error: {str(e)}")
        logging.error(f"Error occurred on line {e.lineno}")
        
        # Print the problematic line and a few lines around it
        with open(os.path.join(current_dir, HTML_TEMPLATE_PATH), 'r', encoding='utf-8') as f:
            template_lines = f.readlines()
        
        start = max(0, e.lineno - 3)
        end = min(len(template_lines), e.lineno + 2)
        
        logging.error("Problematic section of the template:")
        for i in range(start, end):
            logging.error(f"{i+1}: {template_lines[i].rstrip()}")
        
        raise
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        raise

    # ... (rest of the function)

```

This will provide more detailed information about where exactly in the template the error is occurring, which should help in identifying and fixing the issue.

Let me know what you find after implementing these changes, and we can proceed from there to resolve the template syntax error.
