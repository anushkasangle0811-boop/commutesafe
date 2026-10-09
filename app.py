import os
from dotenv import load_dotenv

# Load local development settings before importing modules that read the environment.
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import requests
import secrets

from config import Config
from models import db, User, Contact, SOSAlert, Journey

from email_service import send_journey_email, send_sos_email
from sms_service import send_journey_sms, send_sos_sms

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

NOMINATIM_USER_AGENT = os.getenv(
    "NOMINATIM_USER_AGENT",
    "CommuteSafe/1.0 (+https://commutesafe.onrender.com; contact: anushkasangle0811@gmail.com)",
)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        new_user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            return render_template(
                "login.html",
                error="Invalid email or password. Please try again."
            )

    return render_template("login.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        relation = request.form["relation"]
        email = request.form["email"]

        new_contact = Contact(
            name=name,
            phone=phone,
            relation=relation,
            email=email,
            user_id=session["user_id"]
        )

        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for("mycontacts"))

    return render_template("contact.html")


@app.route("/mycontacts")
def mycontacts():

    if "user_id" not in session:
        return redirect(url_for("login"))

    contacts = Contact.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "mycontacts.html",
        contacts=contacts
    )


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    journey = Journey.query.filter_by(
        user_id=session["user_id"],
        status="active"
    ).order_by(Journey.started_at.desc()).first()

    contacts = Contact.query.filter_by(user_id=session["user_id"]).all()

    recent_journeys = Journey.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Journey.started_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        user=user,
        journey=journey,
        contacts=contacts,
        recent_journeys=recent_journeys
    )


@app.route("/delete_contact/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    contact = Contact.query.filter_by(
        id=contact_id,
        user_id=session["user_id"]
    ).first()

    if contact:
        db.session.delete(contact)
        db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/delete_journey/<int:journey_id>", methods=["POST"])
def delete_journey(journey_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    journey = Journey.query.filter_by(
        id=journey_id,
        user_id=session["user_id"]
    ).first()

    if journey:
        db.session.delete(journey)
        db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/emergency", methods=["GET", "POST"])
def emergency():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.get_json(silent=True) or {}

        lat = data.get("lat")
        lng = data.get("lng")

        if lat is None or lng is None:
            return jsonify({"status": "error", "message": "Location not available"}), 400

        user = User.query.get(session["user_id"])
        contacts = Contact.query.filter_by(user_id=user.id).all()

        location_link = f"https://www.google.com/maps?q={lat},{lng}"

        alert = SOSAlert(
            user_id=session["user_id"],
            latitude=lat,
            longitude=lng
        )
        db.session.add(alert)
        db.session.commit()

        notified = 0

        for contact in contacts:
            try:
                send_sos_email(contact.email, user.name, location_link)
                notified += 1
                print(f"[SOS EMAIL SENT] to {contact.name} ({contact.email})")
            except Exception as e:
                print(f"[SOS EMAIL ERROR] {contact.name}: {e}")

            try:
                send_sos_sms(contact.phone, user.name, location_link)
                print(f"[SOS SMS SENT] to {contact.name} ({contact.phone})")
            except Exception as e:
                print(f"[SOS SMS ERROR] {contact.name}: {e}")

        return jsonify({"status": "sent", "notified": notified}), 200

    return render_template("emergency.html")

@app.route("/send_sos", methods=["POST"])
def send_sos():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}

    lat = data.get("lat") or data.get("latitude")
    lng = data.get("lng") or data.get("longitude")

    if lat is None or lng is None:
        return jsonify({"status": "error", "message": "Location not available"}), 400

    user = User.query.get(session["user_id"])
    contacts = Contact.query.filter_by(user_id=user.id).all()

    location_link = f"https://www.google.com/maps?q={lat},{lng}"

    alert = SOSAlert(
        user_id=session["user_id"],
        latitude=lat,
        longitude=lng
    )
    db.session.add(alert)
    db.session.commit()

    notified = 0

    for contact in contacts:
        try:
            send_sos_email(contact.email, user.name, location_link)
            notified += 1
            print(f"[SOS EMAIL SENT] to {contact.name} ({contact.email})")
        except Exception as e:
            print(f"[SOS EMAIL ERROR] {contact.name}: {e}")

        try:
            send_sos_sms(contact.phone, user.name, location_link)
            print(f"[SOS SMS SENT] to {contact.name} ({contact.phone})")
        except Exception as e:
            print(f"[SOS SMS ERROR] {contact.name}: {e}")

    return jsonify({
        "success": True,
        "message": "Emergency SOS sent successfully.",
        "notified": notified,
        "latitude": lat,
        "longitude": lng
    })

@app.route("/calculate_eta", methods=["POST"])
def calculate_eta():

    if "user_id" not in session:
        return {"error": "Not logged in"}, 401

    data = request.get_json()

    destination = data.get("destination")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not destination or latitude is None or longitude is None:
        return {"error": "Destination and current location are required."}, 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return {"error": "Invalid GPS coordinates."}, 400

    headers = {"User-Agent": NOMINATIM_USER_AGENT, "Accept-Language": "en"}
    geocode_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": destination, "format": "json", "limit": 1}

    try:
        response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as error:
        app.logger.warning("Destination lookup failed: %s", error)
        return {"error": "Unable to find destination right now."}, 500

    if not results:
        return {"error": "Destination not found. Try a more specific place name."}, 404

    destination_lat = float(results[0]["lat"])
    destination_lng = float(results[0]["lon"])

    route_url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{longitude},{latitude};"
        f"{destination_lng},{destination_lat}"
    )

    try:
        route_response = requests.get(route_url, params={"overview": "false"}, timeout=10)
        route_response.raise_for_status()
        route_data = route_response.json()
    except requests.RequestException:
        return {"error": "Unable to calculate route right now."}, 500

    if route_data.get("code") != "Ok":
        return {"error": "Could not calculate a route to this destination."}, 400

    route = route_data["routes"][0]
    distance_meters = route["distance"]
    duration_seconds = route["duration"]
    distance_km = distance_meters / 1000

    base_travel_minutes = max(1, round(duration_seconds / 60))
    safety_buffer = 10
    planned_travel_minutes = base_travel_minutes + safety_buffer

    eta = datetime.now() + timedelta(minutes=planned_travel_minutes)
    arrival_time = eta.strftime("%I:%M %p")

    return {
        "distance_km": round(distance_km, 2),
        "base_travel_time": f"{base_travel_minutes} minutes",
        "safety_buffer": f"{safety_buffer} minutes",
        "travel_time": f"{planned_travel_minutes} minutes",
        "arrival_time": arrival_time
    }


@app.route("/start_journey", methods=["GET", "POST"])
def start_journey():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        destination = request.form.get("destination")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        if not latitude or not longitude:
            return render_template("start_journey.html", error="Please allow location access first.")

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return render_template("start_journey.html", error="Invalid location.")

        if not destination:
            return render_template("start_journey.html", error="Please enter a destination.")

        headers = {"User-Agent": NOMINATIM_USER_AGENT, "Accept-Language": "en"}
        geocode_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": destination, "format": "json", "limit": 1}

        try:
            response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()
        except requests.RequestException as error:
            app.logger.warning("Destination lookup failed: %s", error)
            return render_template("start_journey.html", error="Unable to find destination right now.")

        if not results:
            return render_template("start_journey.html", error="Destination not found. Try a more specific place name.")

        destination_lat = float(results[0]["lat"])
        destination_lng = float(results[0]["lon"])

        route_url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{longitude},{latitude};"
            f"{destination_lng},{destination_lat}"
        )

        try:
            route_response = requests.get(route_url, params={"overview": "false"}, timeout=10)
            route_response.raise_for_status()
            route_data = route_response.json()
        except requests.RequestException:
            return render_template("start_journey.html", error="Unable to calculate route right now.")

        if route_data.get("code") != "Ok":
            return render_template("start_journey.html", error="Could not calculate a route to this destination.")

        duration_seconds = route_data["routes"][0]["duration"]
        base_travel_minutes = max(1, round(duration_seconds / 60))
        safety_buffer = 10
        planned_travel_minutes = base_travel_minutes + safety_buffer
        eta = datetime.now() + timedelta(minutes=planned_travel_minutes)

        tracking_token = secrets.token_urlsafe(32)

        new_journey = Journey(
            user_id=session["user_id"],
            destination=destination,
            eta=eta,
            status="active",
            last_latitude=str(latitude),
            last_longitude=str(longitude),
            last_location_at=datetime.now(),
            tracking_token=tracking_token,
            destination_lat=str(destination_lat),
            destination_lng=str(destination_lng)
        )

        db.session.add(new_journey)
        db.session.commit()

        user = User.query.get(session["user_id"])
        contacts = Contact.query.filter_by(user_id=user.id).all()
        tracking_url = url_for("track_journey", tracking_token=tracking_token, _external=True)

        for contact in contacts:
            try:
                send_journey_email(contact.email, user.name, destination, eta.strftime("%I:%M %p"), tracking_url)
                print(f"[EMAIL SENT] to {contact.name} ({contact.email})")
            except Exception as e:
                print(f"[EMAIL ERROR] {contact.name}: {e}")

            try:
                send_journey_sms(contact.phone, tracking_url, destination)
                print(f"[SMS SENT] to {contact.name} ({contact.phone})")
            except Exception as e:
                print(f"[SMS ERROR] {contact.name}: {e}")

        return redirect(url_for("myjourney"))

    return render_template("start_journey.html")


@app.route("/myjourney")
def myjourney():

    if "user_id" not in session:
        return redirect(url_for("login"))

    journey = Journey.query.filter_by(
        user_id=session["user_id"],
        status="active"
    ).order_by(Journey.started_at.desc()).first()

    return render_template("myjourney.html", journey=journey)


@app.route("/track/<tracking_token>")
def track_journey(tracking_token):

    journey = Journey.query.filter_by(tracking_token=tracking_token).first()

    if not journey:
        return "Invalid or expired tracking link.", 404

    user = User.query.get(journey.user_id)

    return render_template("track_journey.html", journey=journey, user=user)


@app.route("/api/track/<tracking_token>")
def api_track_journey(tracking_token):

    journey = Journey.query.filter_by(tracking_token=tracking_token).first()

    if not journey:
        return {"error": "Invalid tracking link."}, 404

    return {
        "latitude": journey.last_latitude,
        "longitude": journey.last_longitude,
        "status": journey.status,
        "last_location_at": (
            journey.last_location_at.strftime("%d %b %Y, %I:%M %p")
            if journey.last_location_at else None
        )
    }


@app.route("/journey_history")
def journey_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    journeys = Journey.query.filter_by(
        user_id=session["user_id"],
        status="completed"
    ).order_by(Journey.started_at.desc()).all()

    return render_template("journey_history.html", journeys=journeys)


@app.route("/update_journey_location", methods=["POST"])
def update_journey_location():

    if "user_id" not in session:
        return {"error": "Not logged in"}, 401

    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")

    journey = Journey.query.filter_by(
        user_id=session["user_id"],
        status="active"
    ).order_by(Journey.started_at.desc()).first()

    if not journey:
        return {"error": "No active journey"}, 404

    journey.last_latitude = lat
    journey.last_longitude = lng
    journey.last_location_at = datetime.now()

    db.session.commit()

    return {"message": "Journey location updated successfully!"}, 200


@app.route("/complete_journey/<int:journey_id>", methods=["POST"])
def complete_journey(journey_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    journey = Journey.query.filter_by(
        id=journey_id,
        user_id=session["user_id"]
    ).first()

    if journey:
        journey.status = "completed"
        db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/hospitals")
def hospitals():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("hospitals.html")


@app.route("/police")
def police():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("police.html")


@app.route("/medical")
def medical():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("medical.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False), host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
