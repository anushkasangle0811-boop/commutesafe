import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email_alert(to_email, subject, body_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

    return {"success": True}


def send_journey_email(to_email, user_name, destination, eta_time, tracking_url):
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    subject = f"CommuteSafe: {user_name} has started a journey"

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #22262B;">
        <h2 style="color: #16223A;">CommuteSafe Journey Alert</h2>
        <p><b>{user_name}</b> has started a journey.</p>
        <p><b>Destination:</b> {destination}</p>
        <p><b>Started:</b> {now}</p>
        <p><b>Expected arrival:</b> {eta_time}</p>
        <p>
          <a href="{tracking_url}"
             style="background:#16223A;color:white;padding:10px 20px;
                    border-radius:8px;text-decoration:none;">
            Track Live Location
          </a>
        </p>
      </body>
    </html>
    """

    return send_email_alert(to_email, subject, body_html)


def send_sos_email(to_email, user_name, location_link):
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    subject = f"URGENT: SOS Alert from {user_name}"

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #22262B;">
        <h2 style="color: #D6432E;">SOS ALERT</h2>
        <p><b>{user_name}</b> may need immediate help.</p>
        <p><b>Time:</b> {now}</p>
        <p>
          <a href="{location_link}"
             style="background:#D6432E;color:white;padding:10px 20px;
                    border-radius:8px;text-decoration:none;">
            View Current Location
          </a>
        </p>
      </body>
    </html>
    """

    return send_email_alert(to_email, subject, body_html)