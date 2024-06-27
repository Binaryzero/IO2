import argparse
import ipaddress
import json
import os
import re
import socket
import sys
from urllib.parse import urljoin, urlparse

import requests


def is_valid_url(url):
    """
    Check if the given URL is valid.

    :param url: URL to check
    :return: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in [
            "http",
            "https",
        ]
    except ValueError:
        return False


def is_internal_ip(hostname):
    """
    Check if the hostname resolves to an internal IP address.

    :param hostname: Hostname to check
    :return: True if internal IP, False otherwise
    """
    try:
        ip = socket.gethostbyname(hostname)
        return ipaddress.ip_address(ip).is_private
    except (socket.gaierror, ValueError):
        return False


def get_csp_policy(url):
    """
    Retrieve the Content Security Policy from the given URL.

    :param url: URL to check
    :return: CSP header or error message
    """
    if not is_valid_url(url):
        return "Error: Invalid URL format"

    parsed_url = urlparse(url)
    if is_internal_ip(parsed_url.hostname):
        return "Error: Access to internal IP addresses is not allowed"

    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        csp_header = response.headers.get("Content-Security-Policy")
        if csp_header:
            return csp_header
        else:
            return "No CSP header found"
    except requests.RequestException as e:
        return f"Error: {str(e)}"


def parse_csp_policy(csp_header):
    """
    Parse the CSP header into a dictionary.

    :param csp_header: CSP header string
    :return: Dictionary of CSP directives and their values
    """
    if csp_header.startswith("Error:") or csp_header == "No CSP header found":
        return {"error": csp_header}

    policies = {}
    directives = csp_header.split(";")
    for directive in directives:
        if directive.strip():
            key, *values = directive.strip().split()
            policies[key] = values
    return policies


def analyze_csp_policy(policies):
    """
    Analyze the CSP policy for potential issues.

    :param policies: Dictionary of CSP directives and their values
    :return: List of analysis results
    """
    analysis = []

    if "default-src" not in policies:
        analysis.append(
            "Warning: 'default-src' directive is missing. This is recommended as a fallback."
        )

    for directive, values in policies.items():
        if "'unsafe-inline'" in values:
            analysis.append(
                f"Warning: '{directive}' allows 'unsafe-inline', which can be risky."
            )
        if "'unsafe-eval'" in values:
            analysis.append(
                f"Warning: '{directive}' allows 'unsafe-eval', which can be risky."
            )
        if any("*" in value for value in values):
            analysis.append(
                f"Warning: '{directive}' contains a wildcard (*), which may make the policy overly permissive."
            )

    overly_permissive = ["*", "http:", "https:"]
    for directive, values in policies.items():
        if any(source in values for source in overly_permissive):
            analysis.append(f"Warning: '{directive}' has overly permissive sources.")

    return analysis


def sanitize_filename(filename):
    """
    Sanitize the given filename to prevent path traversal.

    :param filename: Filename to sanitize
    :return: Sanitized filename
    """
    sanitized = re.sub(r"[^\w\-_\. ]", "", filename)
    sanitized = sanitized.lstrip(".")
    if not sanitized:
        sanitized = "csp_report"
    return sanitized + ".json"


def save_results(url, policies, analysis, filename):
    """
    Save the CSP policy and analysis results to a file.

    :param url: URL of the checked website
    :param policies: Dictionary of CSP directives and their values
    :param analysis: List of analysis results
    :param filename: Name of the file to save results
    """
    results = {"url": url, "csp_policy": policies, "analysis": analysis}

    safe_filename = os.path.join(os.getcwd(), sanitize_filename(filename))

    with open(safe_filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {safe_filename}")


def main():
    """
    Main function to run the CSP Policy Checker.
    """
    parser = argparse.ArgumentParser(
        description="Check Content Security Policy (CSP) of a website"
    )
    parser.add_argument("url", nargs="?", help="URL of the website to check")
    parser.add_argument("-o", "--output", help="Save results to a file")
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = input("Enter the URL of the website to check: ")

    if not urlparse(url).scheme:
        url = "https://" + url

    print(f"Checking CSP for: {url}")
    csp_header = get_csp_policy(url)
    policies = parse_csp_policy(csp_header)

    print("\nCSP Policy:")
    print(json.dumps(policies, indent=2))

    if isinstance(policies, dict) and "error" not in policies:
        analysis = analyze_csp_policy(policies)
        print("\nAnalysis:")
        for item in analysis:
            print(f"- {item}")
    else:
        analysis = []
        print("\nNo analysis available due to missing or invalid CSP header.")

    if args.output:
        domain = urlparse(url).netloc
        filename = f"{domain}_csp_report.json"
        if args.output != True:
            filename = args.output
        save_results(url, policies, analysis, filename)


if __name__ == "__main__":
    main()
