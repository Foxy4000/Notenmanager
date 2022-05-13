# -*- coding: utf-8 -*-
from flask import Flask, render_template, Blueprint, session, request, flash
from flask_sqlalchemy import SQLAlchemy

#from . import db

#Create a Flask Instance
app = Flask(__name__)
main = Blueprint('main', __name__)
app.secret_key = "secret key"

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#Initialize Database
db = SQLAlchemy(app)


#Create a route decorator
@app.route("/")
def index():
    # session['logged_in'] = False erst wenn der Button geklickt wird (Funktion noch nicht implementiert)
    session['logged_in'] = False
    return render_template("index.html")


@app.route("/login")
def login(): 
    
    session['logged_in'] = True
    return render_template("login.html")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template("index.html")

@app.route("/profile", methods = ['POST', 'GET'])
def profile():
    #session['logged_in'] = True
    if request.form.get('submit1') == 'Schüler hinzufügen':
        vorname = request.form.get('name')
        nachname = request.form.get('surname')
        schueler = Schueler(vorname=vorname, nachname=nachname)
        db.session.add(schueler)
        db.session.commit()
        flash("Schüler wurde hinzugefügt!")
    return render_template("profile.html")


class Lehrer(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    passwort = db.Column(db.String(100), nullable=True)
    vorname = db.Column(db.String(120), nullable=True)
    nachname = db.Column(db.String(120), nullable=True)
    ist_administrator = db.Column(db.Boolean, nullable=True)
    
    
class Schueler(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    vorname = db.Column(db.String(120), nullable=True)
    nachname = db.Column(db.String(120), nullable=True)
    klasse_id = db.Column(db.Integer, nullable=True)


app.run(debug=True)