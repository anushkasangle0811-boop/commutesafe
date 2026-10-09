import os
from datetime import datetime
import requests

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email_alert(to_email, subject, body_html):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    if not api_key or not from_email:
        raise RuntimeError(
            "SendGrid is not configured. Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL."
        )

    response = requests.post(
        SENDGRID_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email, "name": "CommuteSafe"},
            "subject": subject,
            "content": [{"type": "text/html", "value": body_html}],
        },
        timeout=10,
    )
    response.raise_for_status()

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
