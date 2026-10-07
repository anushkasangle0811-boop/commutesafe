import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

def get_twilio_client():
    if not all((TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER)):
        raise RuntimeError("Twilio is not configured. Set the TWILIO_* environment variables.")
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_journey_sms(phone, tracking_url, destination):
    message = get_twilio_client().messages.create(
        body=(
            f"CommuteSafe Alert: A trusted contact has started "
            f"a journey to {destination}. Track here: {tracking_url}"
        ),
        from_=TWILIO_FROM_NUMBER,
        to=phone
    )
    return message.sid


def send_sos_sms(phone, user_name, location_link):
    message = get_twilio_client().messages.create(
        body=(
            f"SOS ALERT from {user_name}! Immediate help may be needed. "
            f"Location: {location_link}"
        ),
        from_=TWILIO_FROM_NUMBER,
        to=phone
    )
    return message.sid
