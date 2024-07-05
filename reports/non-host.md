I apologize for these issues. Let's address both problems:

1. HTML report with unwanted \n characters
2. TypeError in the export_to_powerpoint function

First, let's fix the HTML report issue:



Update the `generate_executive_summary` function to use `textwrap.dedent()` to remove extra whitespace:

```python
import textwrap

def generate_executive_summary(data):
    # ... [previous code remains the same] ...

    html_summary = textwrap.dedent(f"""
    <h2>Executive Summary</h2>
    <p>This report covers {total_vulnerabilities} total vulnerabilities, including {unique_vulnerabilities} unique vulnerabilities across {affected_hosts} hosts/sources.</p>
    <p><strong class="priority-high">Past Due Vulnerabilities: {past_due}</strong></p>
    <ul>
    """).strip()
    
    # ... [rest of the function remains the same] ...

    html_summary += textwrap.dedent("""
    </ul>
    <p>Top Applications by vulnerability count:</p>
    <ul>
    """).strip()
    
    # ... [rest of the function remains the same] ...

    html_summary += textwrap.dedent(f"""
    </ul>
    <p>Immediate action is required to address past due and high-priority vulnerabilities.</p>
    """).strip()

    return html_summary, plain_summary

```

Now, let's address the TypeError in the `export_to_powerpoint` function:



Let's modify the `export_to_powerpoint` function to handle cases where the slide might not have a title shape:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import re

def export_to_powerpoint(exec_summary, output_file='executive_summary.pptx'):
    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # Add title to the slide
    title_shape = slide.shapes.title
    if title_shape is None:
        title_shape = slide.shapes.add_title()
    title_shape.text = "Security Vulnerability Report - Executive Summary"
    
    left = top = Inches(0.5)
    width = Inches(9)
    height = Inches(5)
    
    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True

    # Remove HTML tags and split into lines
    lines = re.sub('<.*?>', '', exec_summary).split('\n')
    
    for line in lines:
        line = line.strip()
        if line:
            p = text_frame.add_paragraph()
            if line.startswith('This report covers'):
                p.text = line
                p.font.size = Pt(12)
            elif line.startswith('Past Due Vulnerabilities:'):
                p.text = line
                p.font.bold = True
                p.font.color.rgb = RGBColor(255, 0, 0)  # Red color for past due
            elif any(line.startswith(priority) for priority in ['Priority 1', 'Priority 2', 'Priority 3']):
                parts = line.split(':')
                p.text = parts[0] + ':'
                p.font.bold = True
                run = p.add_run()
                run.text = ':'.join(parts[1:])
            elif line.startswith('Top Applications'):
                p.text = line
                p.font.bold = True
            elif '(ID:' in line:
                # This is an application line
                p.text = line.split('(ID:')[0].strip()
                p.font.bold = True
                run = p.add_run()
                run.text = '(ID:' + line.split('(ID:')[1]
            elif 'Priority' in line and '|' in line:
                # This is a severity breakdown line
                p.text = line
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.LEFT
                p.space_before = Pt(0)
            elif line.startswith('Immediate action'):
                p.text = line
                p.font.italic = True
            else:
                p.text = line

    prs.save(output_file)
    print(f"Executive summary exported to {output_file}")

```

These changes should resolve both issues:

1. The HTML report should no longer contain unwanted \n characters.
2. The PowerPoint export function should now handle cases where the slide doesn't have a default title shape.

To implement these changes:

1. Update the `generate_executive_summary` function in your script with the new version that uses `textwrap.dedent()`.
2. Replace the existing `export_to_powerpoint` function with the updated version provided above.
3. Make sure to import `textwrap` at the top of your script:
   ```python
   import textwrap
   ```

After making these changes, run your script again. The HTML report should be cleaner, and the PowerPoint export should work without the TypeError.

If you still encounter any issues, please provide more details about the specific error messages or unexpected behavior, and I'll be happy to help further.
