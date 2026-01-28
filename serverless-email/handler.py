import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
# handle email getting request from hospital.service.email_client.py
# serverless function defined
def send_email(event, context):   
    try:
        # Parse JSON payload from Django / client
        data = json.loads(event.get('body', '{}'))
        to_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')

        # Load SMTP config from environment variables (.env via serverless)
        smtp_server = os.environ.get('EMAIL_HOST')          # e.g., smtp.mailtrap.io
        smtp_port = int(os.environ.get('EMAIL_PORT', 587))  # default to 587
        sender_email = os.environ.get('EMAIL_USER')         # your SMTP username
        sender_password = os.environ.get('EMAIL_PASSWORD')  # your SMTP password
        from_email = os.environ.get('EMAIL_FROM', sender_email)  # fallback to sender_email

        # Prepare email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # secure connection
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent successfully to {to_email}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully"})
        }

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
