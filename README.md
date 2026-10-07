# CommuteSafe

CommuteSafe is a Flask app for sharing journey status and location with trusted contacts, with SOS alerts and nearby emergency information.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set a private `SECRET_KEY`.
4. Start the app: `python app.py`
5. Open `http://127.0.0.1:5000`.

SQLite is used locally when `DATABASE_URL` is not set. The local database is created under `database/` and is intentionally excluded from Git.

## Deploy to Render

This repository includes a Render Blueprint (`render.yaml`). In Render, create a new Blueprint from the GitHub repository and provide `DATABASE_URL` for a Render PostgreSQL database. Use a paid database for data that must persist; Render's free PostgreSQL databases expire after 30 days. The Blueprint generates `SECRET_KEY` automatically. Set email and Twilio environment variables if you want those integrations enabled.

The web service uses `pip install -r requirements.txt` to build and `gunicorn app:app` to start. The app creates its tables at startup; schema changes to an existing deployment should be handled with a database migration rather than relying on `create_all()`.

### Alert delivery notes

SMS requires valid `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER` values. Email currently uses Gmail SMTP on port 587. Render's free web services block outbound SMTP on common SMTP ports, including 587, so email alerts need to be moved to an email provider's HTTPS API before they can be relied on from a free Render service. Missing integrations do not prevent the web app from starting, but their alert sends will fail.

## GitHub

Do not commit `.env`, local database files, Python caches, or editor temporary files. Configure `DATABASE_URL`, `SECRET_KEY`, and any integration credentials in Render's environment settings, not in source control.