import smtplib
import os
from email.mime.text import MIMEText

def send_email(to: str, subject: str, body: str) -> str:
    try:
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        if not sender or not password:
            return "Email sending is not configured. Please set EMAIL_USER and EMAIL_PASS in your .env file."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return f"Email sent successfully to {to}."

    except Exception as e:
        print("Email tool error:", e)
        return "Sorry, I couldn't send the email."