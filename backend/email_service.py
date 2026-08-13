import smtplib
import os
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    
    if not sender_email or not password:
        logger.warning("EMAIL_USER or EMAIL_PASS not set. Simulating email send for testing.")
        return
        
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.send_message(msg)
    server.quit()
