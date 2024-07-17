Yes, you can export OneNote notebooks or sections in bulk, which is much more efficient than exporting individual pages. Here's how to do it:

1. Open OneNote desktop application (this method works best with the full desktop version, not the Windows 10 app or web version).

2. Right-click on the notebook or section you want to export in the navigation pane.

3. Select "Export" from the context menu.

4. In the "Export" dialog box:
   - Choose what you want to export: Notebook or Section
   - Select the format: Choose "Word Document (*.docx)"
   - Click "Export"

5. Choose a destination folder where you want to save the exported files.

6. Click "OK" to start the export process.

This will create a folder structure mirroring your OneNote organization, with each page saved as a separate .docx file.

If you have multiple notebooks to export, you'll need to repeat this process for each notebook. Unfortunately, OneNote doesn't provide a built-in way to export multiple notebooks simultaneously.

Once you have all your notebooks exported as .docx files, you can use the Python script I provided earlier to batch convert these .docx files to Markdown format. You might need to adjust the script slightly to handle the folder structure created by OneNote's export.

Here's an updated version of the script that can handle nested folders:



```python
import os
import re
from docx import Document

def convert_docx_to_markdown(docx_path, output_folder):
    # Load the Word document
    doc = Document(docx_path)

    # Extract the text content
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)

    # Basic conversion of some common formatting
    markdown_text = []
    for line in full_text:
        # Convert headers
        if line.startswith('Heading 1'):
            line = f'# {line[10:]}'
        elif line.startswith('Heading 2'):
            line = f'## {line[10:]}'
        elif line.startswith('Heading 3'):
            line = f'### {line[10:]}'
        
        # Convert bold text
        line = re.sub(r'\*\*(.*?)\*\*', r'**\1**', line)
        
        # Convert italic text
        line = re.sub(r'\*(.*?)\*', r'*\1*', line)
        
        markdown_text.append(line)

    # Join the lines and write to a file
    markdown_content = '\n\n'.join(markdown_text)
    
    # Create output filename and folder structure
    rel_path = os.path.relpath(docx_path, input_folder)
    output_path = os.path.join(output_folder, os.path.splitext(rel_path)[0] + '.md')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f'Converted {docx_path} to {output_path}')

def batch_convert(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith('.docx'):
                docx_path = os.path.join(root, filename)
                convert_docx_to_markdown(docx_path, output_folder)

# Usage
input_folder = 'path/to/your/exported/onenote/folders'
output_folder = 'path/to/your/markdown/files'
batch_convert(input_folder, output_folder)

```

To use this updated script:

1. Export your OneNote notebooks or sections as described above.

2. Install the required library if you haven't already:
   - Open a command prompt or terminal
   - Run: `pip install python-docx`

3. Save the script to a file, e.g., `convert_to_markdown.py`

4. Update the `input_folder` variable to point to the folder where you exported your OneNote content, and `output_folder` to where you want the Markdown files.

5. Run the script:
   - Open a command prompt or terminal
   - Navigate to the folder containing the script
   - Run: `python convert_to_markdown.py`

This script will maintain the folder structure of your exported OneNote content, converting all .docx files to Markdown format while preserving the hierarchy.

After conversion, you can open the output folder in Obsidian as a new vault, and your notes should be organized similarly to how they were in OneNote.

Remember that while this method handles basic formatting, some complex OneNote features (like embedded files, drawings, or mathematical equations) may not convert perfectly and might require manual adjustment.
