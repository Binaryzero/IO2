import win32com.client

def send_outlook_email(subject, body, recipients):
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        message = outlook.Application.CreateItem(0)
        message.Subject = subject
        message.HTMLBody = body
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        for recipient in recipients:
            message.Recipients.Add(recipient)
        
        message.Send()
        print(f"Email sent successfully to: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        return False
