import os
import smtplib
import ssl
from email.message import EmailMessage


# Read credentials from environment variables
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_otp_email(receiver_email, otp):

    if not SENDER_EMAIL or not APP_PASSWORD:
        return {
            "status": "error",
            "message": "Email credentials not configured"
        }

    try:
        message = EmailMessage()
        message["Subject"] = "EcoTwin Email Verification OTP"
        message["From"] = SENDER_EMAIL
        message["To"] = receiver_email

        message.set_content(f"""
Hello,

Thank you for registering with EcoTwin.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.

Regards,
EcoTwin Team
""")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(message)

        return {
            "status": "success"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
