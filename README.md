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

Destination lookup uses OpenStreetMap's Nominatim service with the `NOMINATIM_USER_AGENT` identifier defined in `render.yaml`. Searches are user-triggered and must remain below Nominatim's request limit of one request per second.

### Alert delivery notes

SMS requires valid `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER` values. Email alerts use SendGrid's HTTPS API and require `SENDGRID_API_KEY` plus `SENDGRID_FROM_EMAIL`, which must be a verified SendGrid sender address. Missing integrations do not prevent the web app from starting, but their alert sends will fail.

## GitHub

Do not commit `.env`, local database files, Python caches, or editor temporary files. Configure `DATABASE_URL`, `SECRET_KEY`, and any integration credentials in Render's environment settings, not in source control.
