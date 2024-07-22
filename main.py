from config import *
from data_processing import read_csv_data, process_rd_csv
from report_generation import generate_html_report
from email_sender import send_outlook_email

def main():
    # Read vulnerability data
    vulnerability_data = read_csv_data(CSV_FILE_PATH)
    
    # Read and process application deliverables data
    rd_data, owner_summary = process_rd_csv(RD_CSV_FILE_PATH)
    
    # Generate HTML report
    report_html = generate_html_report(vulnerability_data, rd_data, owner_summary)
    
    # Save report to file
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    # Send email
    try:
        send_outlook_email(EMAIL_SUBJECT, report_html, EMAIL_RECIPIENTS)
        print("Report sent successfully via Outlook!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        print(f"The report has been saved as '{OUTPUT_REPORT_PATH}' in the current directory.")

    print("Process completed.")

if __name__ == "__main__":
    main()
