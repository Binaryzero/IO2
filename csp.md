Certainly! I'd be happy to help you add a simple UI to this CSP Policy Checker using Streamlit. Streamlit is a great choice for quickly creating web interfaces for Python scripts. Let's modify the existing script to create a Streamlit app.



```python
import streamlit as st
import argparse
import ipaddress
import json
import os
import re
import socket
import sys
from urllib.parse import urljoin, urlparse

import requests

# Existing functions remain the same
def is_valid_url(url):
    # ... (keep the existing implementation)

def is_internal_ip(hostname):
    # ... (keep the existing implementation)

def get_csp_policy(url):
    # ... (keep the existing implementation)

def parse_csp_policy(csp_header):
    # ... (keep the existing implementation)

def analyze_csp_policy(policies):
    # ... (keep the existing implementation)

# Remove the save_results and sanitize_filename functions as they're not needed for the Streamlit app

# Main Streamlit app
def main():
    st.title("Content Security Policy (CSP) Checker")
    
    url = st.text_input("Enter the URL of the website to check:")
    
    if st.button("Check CSP"):
        if url:
            if not urlparse(url).scheme:
                url = "https://" + url
            
            st.write(f"Checking CSP for: {url}")
            csp_header = get_csp_policy(url)
            policies = parse_csp_policy(csp_header)
            
            st.subheader("CSP Policy:")
            st.json(policies)
            
            if isinstance(policies, dict) and "error" not in policies:
                analysis = analyze_csp_policy(policies)
                st.subheader("Analysis:")
                for item in analysis:
                    st.write(f"- {item}")
            else:
                st.warning("No analysis available due to missing or invalid CSP header.")
        else:
            st.error("Please enter a URL to check.")

if __name__ == "__main__":
    main()

```

To use this Streamlit app version of the CSP Policy Checker, you'll need to follow these steps:

1. Install Streamlit if you haven't already:
   ```
   pip install streamlit
   ```

2. Save the code above in a file named `csp_policy_checker_streamlit.py`.

3. Run the Streamlit app:
   ```
   streamlit run csp_policy_checker_streamlit.py
   ```

This will open a new browser window with the Streamlit app. You can then enter a URL and click the "Check CSP" button to see the CSP policy and analysis.

Key changes made to adapt the script for Streamlit:

1. Imported the Streamlit library.
2. Removed the command-line argument parsing and file saving functionality.
3. Created a Streamlit-based UI in the `main()` function:
   - Added a title and text input for the URL.
   - Used a button to trigger the CSP check.
   - Displayed the results using Streamlit's `st.write()`, `st.json()`, and other methods.

This Streamlit app provides a simple, interactive web interface for your CSP Policy Checker. Users can enter a URL, click a button, and see the results displayed on the page.

Would you like me to explain any part of this code in more detail or make any further modifications?
