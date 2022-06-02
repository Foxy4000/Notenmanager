# -*- coding: utf-8 -*-
import json

from flask import Flask, render_template, Blueprint, session, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# from . import db

# Create a Flask Instance
from sqlalchemy.orm import Session

app = Flask(__name__)
main = Blueprint('main', __name__)
app.config['SECRET_KEY'] = "my super secret key"

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize Database
db = SQLAlchemy(app)

# Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Lehrer.query.get(int(user_id))


# Create a route decorator
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.form.get('submit') == 'Login':
        email = request.form.get('email')
        password = request.form.get('password')
        # Look up User by Email Address
        user = Lehrer.query.filter_by(email=email).first()
        if user:
            # Check hashed password
            if check_password_hash(user.passwort, password):
                # if user.passwort == password:
                login_user(user)
                flash("Login successful!")
                return redirect(url_for('profile'))
            else:
                flash("Wrong Password - TryAgain!")
        else:
            flash("That User does not exist! Try again...")
    return render_template("login.html")


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return render_template("index.html")


@app.route("/register", methods=['POST', 'GET', 'DELETE'])
@login_required
def register():
    if request.form.get('submit5') == 'Account registrieren':
        vorname = request.form.get('firstname')
        nachname = request.form.get('lastname')
        email = request.form.get('email')
        passwort = request.form.get('password')
        lehrer = Lehrer.query.filter_by(email=email).first()
        if lehrer is None:
            # Hash the password
            hashed_pw = generate_password_hash(passwort, "sha256")
            if request.form.get('isadmin') == "on":
                isadmin = True
            else:
                isadmin = False
            lehrer = Lehrer(email=email, passwort=hashed_pw, vorname=vorname, nachname=nachname,
                            ist_administrator=isadmin)
            db.session.add(lehrer)
            db.session.commit()
            flash("Teacher succesfully registrated!")
        else:
            flash("Teacher already registrated")
    return render_template("profile.html")


@app.route("/profile", methods=['POST', 'GET', 'DELETE'])
@login_required
def profile():

    if request.form.get('submit1') == 'Schüler hinzufügen':
        vorname = request.form.get('name')
        nachname = request.form.get('surname')
        # klasse = Klasse.query.order_by(Klasse.id.desc()).first() kann sobald die Klasse weiter definiert ist statt der Zeile drunter eingeführt werden
        klasse_id = request.form.get('klasse_id')  # klasse.id statt der request form
        schueler = Schueler(vorname=vorname, nachname=nachname, klasse_id=klasse_id)
        db.session.add(schueler)
        db.session.commit()
        
        flash(vorname + " " + nachname + " wurde hinzugefügt!")
        schueler = Schueler.query.order_by(Schueler.id.desc()).first()
        schueler_id = schueler.id

        if request.form.getlist('fach_id'):
            faecher = request.form.getlist('fach_id')
            for fach_id in faecher:
                belegung = Belegung(schueler_id=schueler_id, fach_id=fach_id)
                db.session.add(belegung)
                db.session.commit()

        if request.form.get('deutsch') == 'Deutsch':
            fach_id = request.form.get('deutsch')
            belegung = Belegung(schueler_id=schueler_id, fach_id=fach_id)
            db.session.add(belegung)
            db.session.commit()



    if request.form.get('submit1') == 'Fach hinzufügen':
        bezeichnung = request.form.get('bezeichnung')
        lehrer_vorname = request.form.get('lehrer_vorname')
        lehrer_nachname = request.form.get('lehrer_nachname')
        lehrer = Lehrer.query.filter_by(vorname=lehrer_vorname, nachname=lehrer_nachname).first()
        fach = Fach(bezeichnung=bezeichnung, lehrer_id=lehrer.id)
        db.session.add(fach)
        db.session.commit()

        flash(bezeichnung + " wurde hinzugefügt!")
        fach = Fach.query.order_by(Fach.id.desc()).first()
        fach_id = fach.id

        if request.form.getlist('schueler_id'):
            schuelerLi = request.form.getlist('schueler_id')
            for schueler_id in schuelerLi:
                belegung = Belegung(schueler_id=schueler_id, fach_id=fach_id)
                db.session.add(belegung)
                db.session.commit()

        if request.form.getlist('pruefung_id'):
            pruefungLi = request.form.getlist('pruefung_id')
            for pruefung_id in pruefungLi:
                checkPruefung = Pruefung.query.get_or_404(pruefung_id)
                checkPruefung.fach_id = fach_id
                db.session.add(checkPruefung)
                db.session.commit()


#Klasse anlegen
    if request.form.get('submit1') == 'Klasse hinzufügen':
        bezeichnung = request.form.get('bezeichnung')
        lehrer_vorname = request.form.get('lehrer_vorname')
        lehrer_nachname = request.form.get('lehrer_nachname')
        lehrer = Lehrer.query.filter_by(vorname=lehrer_vorname, nachname=lehrer_nachname).first()
        klasse = Klasse(bezeichnung=bezeichnung, lehrer_id=lehrer.id)
        db.session.add(klasse)
        db.session.commit()

        flash(bezeichnung + " wurde hinzugefügt!")
        klasse = Klasse.query.order_by(Klasse.id.desc()).first()
        klasse_id = klasse.id

        # if request.form.getlist('schueler_id'):
        #     schuelerLi = request.form.getlist('schueler_id')
        #     for schueler in schuelerLi:
        #     schueler.klasse_id = klasse.id

    belegungListe = Belegung.query.all()
    klassenListe = Klasse.query.all()
    faecherListe = Fach.query.all()
    faecherBesucht = []
    faecherNichtBesucht = []
    schuelerList = Schueler.query.all()
    pruefungListe = Pruefung.query.all()
    lehrer = Lehrer.query.get_or_404(current_user.id)

    # students= Session.query(Lehrer, Schueler, Klasse).filter(Lehrer.id== Klasse.lehrer_id ).filter(Schueler.klasse_id==Klasse.id).all()
    return render_template("profile.html", pruefungListe=pruefungListe, schuelerList=schuelerList, klassenListe=klassenListe, belegungListe=belegungListe, faecherListe=faecherListe, faecherBesucht=faecherBesucht, faecherNichtBesucht=faecherNichtBesucht, lehrer=lehrer)


@app.route('/profile/viewStudent/<student_id>', methods=['GET', 'POST'])
def viewStudent(student_id):
    schueler = Schueler.query.get_or_404(student_id)
    faecher = db.session.query(Schueler, Belegung, Fach
                            ).filter(
                                Schueler.id == Belegung.schueler_id
                            ).filter(
                                Belegung.fach_id == Fach.id
                            ).filter(
                                Schueler.id == student_id)
    return render_template("studentdashboard.html", schueler=schueler, faecher=faecher)


@app.route('/profile/editStudent/<student_id>', methods=['POST', 'GET'])
def editStudent(student_id):
    schueler = Schueler.query.get_or_404(student_id)
    schueler_alt = schueler
    belegungen = Belegung.query.filter_by(schueler_id=student_id)
    if request.method == 'POST':
        firstname = request.form.get('vorname')
        lastname = request.form.get('nachname')
        klasse_id = request.form.get('klasse_id')
        faecher = request.form.getlist('fach_id')
        for belegung in belegungen:
            db.session.delete(belegung)
            db.session.commit()

        for fach_id in faecher:
            belegung = Belegung(fach_id=fach_id, schueler_id=student_id)
            db.session.add(belegung)
            db.session.commit()
        schueler.vorname = firstname
        schueler.nachname = lastname
        schueler.klasse_id = klasse_id
        db.session.add(schueler)
        db.session.commit()
        flash(schueler_alt.vorname + " " + schueler_alt.nachname + " wurde bearbeitet")

    return redirect(url_for('profile'))

# @app.route("/createClass", methods=['POST', 'GET'])
# @login_required
# def createClass():
#     if request.form.get('submit2') == 'Klasse erstellen':
#         if current_user.ist_administrator:
#             klassenname = request.form.get('className')
#             klassenlehrer = request.form.get('classTeacher')
#             lehrerId = Lehrer.query.filter_by(bezeichnung=klassenlehrer)
#             klasse = Klasse(bezeichnung=klassenname, lehrer_id=lehrerId)
#             db.session.add(klasse)
#             db.session.commit()
#
#             klasse = Klasse.query.order_by(Klasse.id.desc()).first()
#             klasse_id = klasse.id
#
#             studentList = request.form.getList('student_id')
#             for student in studentList:
#                 student.class_id = klasse_id
#                 db.session.commit()
#
#             flash("Klasse " + klasse.bezeichnung + " wurde hinzugefügt")
#         else:
#             flash("Keine Berechtigung!")
#
#         classList = Klasse.query.all()
#         return render_template("profile.html", klassenListe=classList)

#@app.route("/createSubject", methods=['POST', 'GET'])
#@login_required
#def createSubject():
#    if request.form.get('submit1') == 'Änderungen speichern':
#        if current_user.ist_administrator:
#            bezeichnung = request.form.get('subjectName')
#            lehrer_bez = request.form.get('subjectTeacher')
#            lehrer = Lehrer.query.filter_by(bezeichnung=lehrer_bez)
#            subject = Fach(bezeichnung=bezeichnung, lehrer_id=lehrer.id)
#            db.session.add(subject)
#            db.session.commit()
#
#            subject = Fach.query.order_by(Fach.id.desc()).first()
#            subject_id = subject.id
#
#            # in der Suche müssen Vorschläge anhand der bisherigen Eingaben gemacht werden
#           # über die Suche gefundene und hinzuzufügende Studenten und Prüfungen müssen in Liste gespeichert werden
#
#            studentList = request.form.get('studentsInSubject')
#            for student in studentList:
#                belegung = Belegung(schueler_id=student.id, fach_id=subject_id)
#                db.session.add(belegung)
#                db.session.commit()
#
#            examList = request.form.get('examsInSubject')
#            for exam in examList:
#                pruefung = Fach.query.get_or_404(exam.id)
#                #if pruefung.fach_id is None:
#                pruefung.fach_id = subject_id
#                db.session.add(pruefung)
#                db.session.commit()
#                #else:...
#
#            flash("Fach " + subject.bezeichnung + " wurde hinzugefügt")
#        else:
#            flash("Keine Berechtigung!")
#
#    subjectList = Fach.query.all()
#    return render_template("profile.html", subjectList=subjectList)


@app.route('/profile/deleteStudent/<student_id>', methods=['POST'])
@login_required
def deleteStudent(student_id):
    schueler = Schueler.query.get_or_404(student_id)
    # belegungen = Belegung.query.filter.by(schueler_id=student_id)
    # bewertungen = Bewertung.query.filter.by(schueler_id=student_id)
    db.session.delete(schueler)
    db.session.commit()
    flash(schueler.vorname + " " + schueler.nachname + " wurde entfernt")
    return redirect(url_for('profile'))


@app.route('/profile/deleteClass/<klasse_id>', methods=['POST', 'GET'])
@login_required
def deleteClass(klasse_id):
    if current_user.ist_administrator:
        schuelerListe = Schueler.query.filter_by(klasse_id=klasse_id)
        for schueler in schuelerListe:
            schueler.klasse_id = None
            db.session.add(schueler)
            db.session.commit(schueler)
        klasse = Klasse.query.get_or_404(klasse_id)
        db.session.delete(klasse)
        db.session.commit()
        flash("Klasse " + klasse.bezeichnung + " wurde entfernt")
    else:
        flash("Keine Berechtigung!")
    return redirect(url_for('profile'))

@app.route('/profile/deleteSubject/<subject_id>', methods=['POST'])
@login_required
def deleteSubject(subject_id):
    fach = Fach.query.get_or_404(subject_id)
    db.session.delete(fach)
    db.session.commit()
    flash("Das Fach " + fach.bezeichnung + " wurde entfernt")
    return redirect(url_for('profile'))


class Lehrer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    passwort = db.Column(db.String(100), nullable=True)
    vorname = db.Column(db.String(120), nullable=True)
    nachname = db.Column(db.String(120), nullable=True)
    ist_administrator = db.Column(db.Boolean, nullable=True)

    # Passwort
    # @property
    # def passwort(self):
    #   raise AttributeError('Password is not a readable Attribute!')

    # @passwort.setter
    # def passwort(self, pwd):
    #   self.passwort = generate_password_hash(pwd)

    # def verify_password(self, pwd):
    #   return check_password_hash(self.passwort, pwd)


class Schueler(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    vorname = db.Column(db.String(120), nullable=True)
    nachname = db.Column(db.String(120), nullable=True)
    klasse_id = db.Column(db.Integer, db.ForeignKey('klasse.id'), nullable=True)  # foreign key of class


class Belegung(db.Model):
    schueler_id = db.Column(db.Integer, nullable=True, primary_key=True)  # primary key of student
    fach_id = db.Column(db.Integer, nullable=True, primary_key=True)  # primary key of course


class Klasse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(100), unique=True)
    lehrer_id = db.Column(db.Integer, nullable=True)  # foreign key of teacher


class Bewertung(db.Model):
    fach_id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, primary_key=True)
    punkte = db.Column(db.Integer, nullable=True)


class Fach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(100), unique=True)
    lehrer_id = db.Column(db.Integer, nullable=True)  # foreign key of teacher


class Pruefung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(100), unique=True)
    notizen = db.Column(db.String(100), unique=True)
    fach_id = db.Column(db.Integer, primary_key=True)



app.run(debug=True)
