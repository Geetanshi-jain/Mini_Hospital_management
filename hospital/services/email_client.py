import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailClient:
    @staticmethod
    def send_email(to_email, subject, body, email_type='generic'):
        """
        Sends email via Serverless Lambda Function
        """
        url = settings.EMAIL_SERVICE_URL
        if not url:
            logger.warning("Email service URL not configured")
            return
            
        payload = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "type": email_type
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
