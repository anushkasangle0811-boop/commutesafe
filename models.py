from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    relation = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='contacts')

    def __repr__(self):
        return f"<Contact {self.name}>"

class SOSAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    triggered_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref='sos_alerts')

    def __repr__(self):
        return f"<SOSAlert {self.id}>"

class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    destination = db.Column(db.String(200), nullable=False)
    eta = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(20), default="active")
    started_at = db.Column(db.DateTime, default=db.func.now())

    last_latitude = db.Column(db.String(50), nullable=True)
    last_longitude = db.Column(db.String(50), nullable=True)
    last_location_at = db.Column(db.DateTime, nullable=True)
    destination_lat = db.Column(db.String(50), nullable=True)
    destination_lng = db.Column(db.String(50), nullable=True)

    tracking_token = db.Column(db.String(100), unique=True, nullable=True)

    user = db.relationship('User', backref='journeys')

    def __repr__(self):
        return f"<Journey {self.destination}>"

   