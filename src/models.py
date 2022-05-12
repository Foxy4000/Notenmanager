
from app import db

class Lehrer(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    passwort = db.Column(db.String(100), nullable=True)
    vorname = db.Column(db.String(120), nullable=True)
    nachname = db.Column(db.String(120), nullable=True)
    ist_administrator = db.Column(db.Boolean, nullable=True)