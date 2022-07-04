# -*- coding: utf-8 -*-
import csv
import tkinter as tk
import ast
from tkinter import filedialog

from flask import Flask, render_template, Blueprint, request, flash, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from flask_csv import send_csv
from tkinter import filedialog
from pickle import NONE
from sqlalchemy.sql.expression import null
from collections.abc import Iterator

# Create a Flask Instance
app = Flask(__name__)
main = Blueprint('main', __name__)
# Secret-Key for user password hash
app.config['SECRET_KEY'] = "my super secret key"

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize Database
db = SQLAlchemy(app)

# Filetypes for export
filetypes = (
    ('CSV', '*.csv'),
    ('All files', '*.*'),
)

# Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#Encrypt function for personal User and Student data
def encrypt(string_value):
    
    string_value = string_value.replace("e", "•")
    string_value = string_value.replace("n", "/")
    string_value = string_value.replace("i", ",")
    string_value = string_value.replace("s", "€")
    string_value = string_value.replace("r", "─")
    string_value = string_value.replace("u", "2")    
    string_value = string_value.replace("t", "9")  
    string_value = string_value.replace("a", "4")     
    string_value = string_value.replace("d", "!")       
    string_value = string_value.replace("h", "5")  
        
    encrypted_string_value = []
    for character in string_value:
        encrypted_string_value.append(ord(character))   
    return(str(encrypted_string_value))

#Decrypt function for personal User and Student data
def decrypt(encrypted_string_value):
    decrypted_string_value = ""
    encrypted_string_value = ast.literal_eval(encrypted_string_value)
    for ascii_value in encrypted_string_value:
        decrypted_string_value = decrypted_string_value + chr(ascii_value)
    
    decrypted_string_value = decrypted_string_value.replace("•", "e")    
    decrypted_string_value = decrypted_string_value.replace("/", "n") 
    decrypted_string_value = decrypted_string_value.replace(",", "i") 
    decrypted_string_value = decrypted_string_value.replace("€", "s") 
    decrypted_string_value = decrypted_string_value.replace("─", "r")
    decrypted_string_value = decrypted_string_value.replace("2", "u")    
    decrypted_string_value = decrypted_string_value.replace("9", "t") 
    decrypted_string_value = decrypted_string_value.replace("4", "a") 
    decrypted_string_value = decrypted_string_value.replace("!", "d") 
    decrypted_string_value = decrypted_string_value.replace("5", "h")    
    
    return(decrypted_string_value)


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
        email = encrypt(email)
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
        vorname = encrypt(vorname)
        nachname = request.form.get('lastname')
        nachname = encrypt(nachname)
        email = request.form.get('email')
        email = encrypt(email)
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
            flash("Teacher successfully registrated!")
        else:
            flash("Teacher already registrated")
    return redirect(url_for('profile'))


@app.route('/profile/editUserData', methods=['POST', 'GET'])
@login_required
def editUserData():
    lehrer = Lehrer.query.get_or_404(current_user.id)
    lehrer.vorname = decrypt(lehrer.vorname)
    lehrer.nachname = decrypt(lehrer.nachname)
    if request.method == 'POST':
        lehrer.vorname = request.form.get('vorname')
        lehrer.vorname = encrypt(lehrer.vorname)
        lehrer.nachname = request.form.get('nachname')
        lehrer.nachname = encrypt(lehrer.nachname)
        lehrer.email = request.form.get('email')
        lehrer.email = encrypt(lehrer.email)
        passwort = request.form.get('passwort')
        # Hash the password
        lehrer.passwort = generate_password_hash(passwort, "sha256")
        if lehrer.ist_administrator:
            lehrer.ist_administrator = True
        else:
            lehrer.ist_administrator = False
        db.session.add(lehrer)
        db.session.commit()
        flash("Profile successfully edited.")

    belegungListe = Belegung.query.all()
    klassenListe = Klasse.query.all()
    faecherListe = Fach.query.all()
    bewertungsListe = Bewertung.query.all()
    faecherBesucht = []
    faecherNichtBesucht = []
    schuelerList = Schueler.query.all()
    for s in schuelerList:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    pruefungListe = Pruefung.query.all()
    lehrerListe = Lehrer.query.all()
    for l in lehrerListe:
        l.vorname = decrypt(l.vorname)
        l.nachname = decrypt(l.nachname)
        l.email = decrypt(l.email)
    origin = "profile"

    # students= Session.query(Lehrer, Schueler, Klasse).filter(Lehrer.id== Klasse.lehrer_id ).filter(Schueler.klasse_id==Klasse.id).all()
    return render_template("profile.html", pruefungListe=pruefungListe, schuelerList=schuelerList,
                           klassenListe=klassenListe, belegungListe=belegungListe, faecherListe=faecherListe,
                           faecherBesucht=faecherBesucht, faecherNichtBesucht=faecherNichtBesucht, lehrer=lehrer,
                           lehrerListe=lehrerListe, bewertungsListe=bewertungsListe, origin=origin)


@app.route("/profile", methods=['POST', 'GET', 'DELETE'])
@login_required
def profile():

    if request.form.get('submit1') == 'Schüler hinzufügen':
        vorname = request.form.get('name')
        vorname = encrypt(vorname)
        nachname = request.form.get('surname')
        nachname = encrypt(nachname)
        # klasse = Klasse.query.order_by(Klasse.id.desc()).first() kann sobald die Klasse weiter definiert ist statt der Zeile drunter eingeführt werden
        klasse_id = request.form.get('klasse_id')  # klasse.id statt der request form
        schueler = Schueler(vorname=vorname, nachname=nachname, klasse_id=klasse_id)
        db.session.add(schueler)
        db.session.commit()

        flash(decrypt(vorname) + " " + decrypt(nachname) + " wurde hinzugefügt!")
        schueler = Schueler.query.order_by(Schueler.id.desc()).first()
        schueler_id = schueler.id

        if request.form.getlist('fach_id'):
            faecher = request.form.getlist('fach_id')
            for fach_id in faecher:
                belegung = Belegung(schueler_id=schueler_id, fach_id=fach_id)
                db.session.add(belegung)
                db.session.commit()

    if request.form.get('submit1') == 'Fach hinzufügen':
        bezeichnung = request.form.get('bezeichnung')
        lehrer_id = request.form.get('klasse_lehrer')
        fach = Fach(bezeichnung=bezeichnung, lehrer_id=lehrer_id)
        db.session.add(fach)
        db.session.commit()

        flash(bezeichnung + " wurde hinzugefügt!")
        fach = Fach.query.order_by(Fach.id.desc()).first()
        fach_id = fach.id

        if request.form.getlist('fach_schueler'):
            schuelerListe = request.form.getlist('fach_schueler')
            for schueler_id in schuelerListe:
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

    # Klasse anlegen
    if request.form.get('submit1') == 'Klasse hinzufügen':
        bezeichnung = request.form.get('bezeichnung')
        lehrer_id = request.form.get('klasse_lehrer')
        klasse = Klasse(bezeichnung=bezeichnung, lehrer_id=lehrer_id)
        db.session.add(klasse)
        db.session.commit()

        flash(bezeichnung + " wurde hinzugefügt!")
        klasse = Klasse.query.order_by(Klasse.id.desc()).first()
        klasse_id = klasse.id

        if request.form.getlist('klasse_schueler'):
            schuelerListe = request.form.getlist('klasse_schueler')
            for schueler_id in schuelerListe:
                student = Schueler.query.get_or_404(schueler_id)
                student.klasse_id = klasse_id
                db.session.add(student)
                db.session.commit()

            db.session.commit()
    if request.form.get('submit1') == 'Prüfung hinzufügen':
        bezeichnung = request.form.get('bezeichnung')
        notizen = request.form.get('beschreibung')
        fach_id = request.form.get('fach_id')
        pruefung = Pruefung(bezeichnung=bezeichnung, notizen=notizen, fach_id=fach_id)
        db.session.add(pruefung)
        db.session.commit()
        pruefung = Pruefung.query.order_by(Pruefung.id.desc()).first()
        pruefung_id = pruefung.id
        bewertungListe = request.form.getlist('examStudent')
        notenliste = request.form.getlist('achievedPoints')
        for schuelerId in bewertungListe:
            id = schuelerId
            note = notenliste[bewertungListe.index(schuelerId)]

            if note is not '':
                note = float(note.replace(",","."))
                bewertung = Bewertung(pruefung_id=pruefung_id, schueler_id=id, punkte=note)
            else:
                bewertung = Bewertung(pruefung_id=pruefung_id, schueler_id=id, punkte=None)
            db.session.add(bewertung)
            db.session.commit()
        punkteObergrenze = request.form.getlist('punkteObergrenze')
        i = 1
        for punkte in punkteObergrenze:
            notenschluessel = Notenschluessel(note=i, punkte_obergrenze=punkte, pruefung_id=pruefung_id)
            i = i + 1
            db.session.add(notenschluessel)
            db.session.commit()

    belegungListe = Belegung.query.all()
    klassenListe = Klasse.query.all()
    faecherListe = Fach.query.all()
    bewertungsListe = Bewertung.query.all()
    faecherBesucht = []
    faecherNichtBesucht = []
    schuelerList = Schueler.query.all()
    for s in schuelerList:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    lehrerListe = Lehrer.query.all()
    for l in lehrerListe:
        l.vorname = decrypt(l.vorname)
        l.nachname = decrypt(l.nachname)
        l.email = decrypt(l.email)
    pruefungListe = Pruefung.query.all()
    lehrer = Lehrer.query.get_or_404(current_user.id)

    origin = "profile"

    # students= Session.query(Lehrer, Schueler, Klasse).filter(Lehrer.id== Klasse.lehrer_id ).filter(Schueler.klasse_id==Klasse.id).all()
    return render_template("profile.html", pruefungListe=pruefungListe, schuelerList=schuelerList,
                           klassenListe=klassenListe, belegungListe=belegungListe, faecherListe=faecherListe,
                           faecherBesucht=faecherBesucht, faecherNichtBesucht=faecherNichtBesucht, lehrer=lehrer,
                           lehrerListe=lehrerListe, bewertungsListe=bewertungsListe, origin=origin)


@app.route("/profile/exportStudentList/<class_id>", methods=['GET', 'POST'])
@login_required
def exportStudentList(class_id):
    klasse = Klasse.query.get_or_404(class_id)

    filename = tk.filedialog.asksaveasfilename(
        title='Speichern als...',
        filetypes=filetypes,
        defaultextension='.csv'
    )

    if filename != '':
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            schuelerListe = Schueler.query.filter_by(klasse_id=class_id)
            lehrerListe = Lehrer.query.all()
            lehrer = None
            for lehrerAusListe in lehrerListe:
                if lehrerAusListe.id == klasse.lehrer_id:
                    lehrer = lehrerAusListe

            csvwriter.writerow(["Klasse:", klasse.bezeichnung])
            csvwriter.writerow(["Lehrer:", decrypt(lehrer.vorname), decrypt(lehrer.nachname)])
            csvwriter.writerow([])
            csvwriter.writerow(["Vorname", "Nachname"])

            for schueler in schuelerListe:
                csvwriter.writerow([decrypt(schueler.vorname), decrypt(schueler.nachname)])
            flash("Schülerliste wurden exportiert")
    return redirect(url_for('profile'))


class hn_wrapper(Iterator):
  def __init__(self, it):
    self.it = iter(it)
    self._hasnext = None
    
  def __iter__(self): 
    return self
  
  def __next__(self):
    if self._hasnext:
      result = self._thenext
    else:
      result = next(self.it)
    self._hasnext = None
    return result
  
  def hasnext(self):
    if self._hasnext is None:
      try: 
        self._thenext = next(self.it)
      except StopIteration: 
        self._hasnext = False
      else: self._hasnext = True
    return self._hasnext


@app.route("/profile/exportGradelist/<pruefung_id>", methods=['GET', 'POST'])
@login_required
def exportGradelist(pruefung_id):
    pruefung = Pruefung.query.get_or_404(pruefung_id)
    fach = Fach.query.get_or_404(pruefung.fach_id)
    bewertungen = Bewertung.query.filter_by(pruefung_id=pruefung_id)
    notenschluessel = Notenschluessel.query.filter_by(pruefung_id=pruefung_id)

    filename = tk.filedialog.asksaveasfilename(
        title='Speichern als...',
        filetypes=filetypes,
        defaultextension='.csv'
    )

    if filename != '':
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')

            
            csvwriter.writerow(["Fach:", fach.bezeichnung])
            csvwriter.writerow(["Prüfung:", pruefung.bezeichnung])
            csvwriter.writerow([])
            csvwriter.writerow(["Vorname", "Nachname", "Punkte", "Note"])

            for bewertung in bewertungen:
                schueler = Schueler.query.get_or_404(bewertung.schueler_id)
                
                note=""
                notenschluesselIt = hn_wrapper(notenschluessel)
                for ns in notenschluesselIt:
                    if bewertung.punkte <= ns.punkte_obergrenze:
                        if notenschluesselIt.hasnext():
                            nsNext = next(notenschluesselIt)
                            if bewertung.punkte > nsNext.punkte_obergrenze:
                                note = ns.note
                            else:
                                note = nsNext.note
                        
                
                csvwriter.writerow([decrypt(schueler.vorname), decrypt(schueler.nachname), str(bewertung.punkte).replace(".",","), note])
            flash("Notenliste wurden exportiert")
    return redirect(url_for('profile'))


@app.route("/profile/searchStudent", methods=['GET', 'POST'])
@login_required
def searchStudent():
    student_id = request.form.get('searched')
    if student_id is not None:
        return redirect(url_for('viewStudent', student_id=student_id))
    else:
        flash("Funktioniert noch nicht")
    return redirect(url_for('profile'))


@app.route('/profile/viewStudent/<student_id>', methods=['GET', 'POST'])
@login_required
def viewStudent(student_id):
    

    schuelerListe = Schueler.query.all()
    for s in schuelerListe:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    schueler = Schueler.query.get_or_404(student_id)
    klassenListe = Klasse.query.all()
    faecherListe = Fach.query.all()
    notenschluesselListe = Notenschluessel.query.all()
    belegungListe = Belegung.query.filter_by(schueler_id=schueler.id)
    faecherBesucht = []
    faecherNichtBesucht = []
    pruefungen = db.session.query(Schueler, Belegung, Pruefung
                                  ).filter(
        Schueler.id == Belegung.schueler_id
    ).filter(
        Belegung.fach_id == Pruefung.fach_id
    ).filter(
        Schueler.id == student_id
    ).all()

    faecher = db.session.query(Schueler, Belegung, Fach
                               ).filter(
        Schueler.id == Belegung.schueler_id
    ).filter(
        Belegung.fach_id == Fach.id
    ).filter(
        Schueler.id == student_id
    ).all()
    origin = "viewStudent"
    bewertung = db.session.query(Schueler, Bewertung).filter(Schueler.id == Bewertung.schueler_id).filter(
        Schueler.id == student_id).all()
    return render_template("studentdashboard.html", schueler=schueler, faecher=faecher, schuelerList=schuelerListe,
                           faecherListe=faecherListe, klassenListe=klassenListe, faecherBesucht=faecherBesucht,
                           faecherNichtBesucht=faecherNichtBesucht, pruefungen=pruefungen, bewertungen=bewertung,
                           origin=origin, notenschluesselListe=notenschluesselListe, belegungListe=belegungListe)


@app.route('/profile/editStudent/<student_id>', methods=['POST', 'GET'])
@login_required
def editStudent(student_id):
    schueler = Schueler.query.get_or_404(student_id)
    schueler_alt = schueler
    belegungen = Belegung.query.filter_by(schueler_id=student_id)
    origin = None
    if request.method == 'POST':
        origin = request.form.get('origin')
        firstname = request.form.get('vorname')
        firstname = encrypt(firstname)
        lastname = request.form.get('nachname')
        lastname = encrypt(lastname)
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
        flash(decrypt(schueler_alt.vorname) + " " + decrypt(schueler_alt.nachname) + " wurde bearbeitet")
    if origin == "profile":
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('viewStudent', student_id=student_id))


@app.route('/profile/editClass/<klasse_id>', methods=['POST', 'GET'])
def editClass(klasse_id):
    origin = None
    if request.method == 'POST':
        klasse = Klasse.query.get_or_404(klasse_id)
        origin = request.form.get('origin')
        bezeichnung = request.form.get('bezeichnung')
        klasse.bezeichnung = bezeichnung

        if request.form.get('klasse_lehrer'):
            lehrer_id = request.form.get('klasse_lehrer')
            klasse.lehrer_id = lehrer_id

        db.session.add(klasse)
        db.session.commit()

        if request.form.getlist('klasse_schueler'):
            schuelerListe = Schueler.query.filter_by(klasse_id=klasse_id)
            for schueler in schuelerListe:
                schueler.klasse_id = None
                db.session.add(schueler)
                db.session.commit()
            schuelerListe_id = request.form.getlist('klasse_schueler')
            for schueler_id in schuelerListe_id:
                schueler = Schueler.query.get_or_404(schueler_id)
                schueler.klasse_id = klasse_id
                db.session.add(schueler)
                db.session.commit()
        flash(klasse.bezeichnung + " wurde bearbeitet")

    if origin == "profile":
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('viewClass', klasse_id=klasse_id))


@app.route('/profile/viewClass/editExam/<pruefung_id>', methods=['POST', 'GET'])
@login_required
def editExam(pruefung_id):
    pruefung = Pruefung.query.get_or_404(pruefung_id)
    bezeichnung = request.form.get('bezeichnung')
    notizen = request.form.get('beschreibung')
    pruefung.notizen = notizen
    db.session.add(pruefung)
    db.session.commit()

    notenschluesselListe = Notenschluessel.query.filter_by(pruefung_id=pruefung_id)
    punkteObergrenze = request.form.getlist('punkteObergrenze')
    i = 1
    for punkte in punkteObergrenze:
        for notenschluessel in notenschluesselListe:
            if notenschluessel.note == i:
                notenschluessel.punkte_obergrenze = punkte
        i = i + 1
        db.session.add(notenschluessel)
        db.session.commit()

    schuelerListe = request.form.getlist('examStudent')
    punkteListe = request.form.getlist('achievedPoints')
    bewertungListe = Bewertung.query.filter_by(pruefung_id=pruefung_id)
    laenge = len(schuelerListe)

    schuelerListe_ID = []
    for schueler in schuelerListe:
        schueler_id = int(schueler)
        schuelerListe_ID.append(schueler_id)

    bewertungListe_ID = []
    for bewertung in bewertungListe:
        schueler_id = bewertung.schueler_id
        bewertungListe_ID.append(schueler_id)

    for schueler_id in schuelerListe_ID:
        if schueler_id not in bewertungListe_ID:
            bewertung = Bewertung(pruefung_id=pruefung_id, schueler_id=schueler_id, punkte=null)
            db.session.add(bewertung)
            db.session.commit()

    bewertungListe = Bewertung.query.filter_by(pruefung_id=pruefung_id)

    for i in range(0, laenge):
        punkte = punkteListe[i]
        schueler_id = int(schuelerListe[i])
        for bewertung in bewertungListe:
            if schueler_id == bewertung.schueler_id and punkte is not '' and punkte is not null:
                bewertung.punkte = float(punkte.replace(",","."))
                db.session.add(bewertung)
                db.session.commit()

    return redirect(url_for('profile'))


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
            db.session.commit()
        klasse = Klasse.query.get_or_404(klasse_id)
        db.session.delete(klasse)
        db.session.commit()
        flash("Klasse " + klasse.bezeichnung + " wurde entfernt")
    else:
        flash("Keine Berechtigung!")
    return redirect(url_for('profile'))


@app.route('/profile/deletePruefung/<pruefung_id>', methods=['POST', 'GET'])
@login_required
def deletePruefung(pruefung_id):
    bewertungListe = Bewertung.query.filter_by(pruefung_id=pruefung_id)
    for bewertung in bewertungListe:
        db.session.delete(bewertung)
        db.session.commit()
    pruefung = Pruefung.query.get_or_404(pruefung_id)
    db.session.delete(pruefung)
    db.session.commit()
    flash("Prüfung " + pruefung.bezeichnung + " wurde entfernt.")
    return redirect(url_for('profile'))


@app.route('/profile/editSubject/<fach_id>', methods=['POST', 'GET'])
@login_required
def editSubject(fach_id):
    origin = None
    if request.method == 'POST':
        origin = request.form.get('origin')
        fach = Fach.query.get_or_404(fach_id)
        bezeichnung = request.form.get('bezeichnung')
        fach.bezeichnung = bezeichnung

        if request.form.get('fach_lehrer'):
            lehrer_id = request.form.get('fach_lehrer')
            fach.lehrer_id = lehrer_id

        db.session.add(fach)
        db.session.commit()

        if request.form.get('fach_schueler'):
            belegungListe = Belegung.query.filter_by(fach_id=fach_id)
            for belegung in belegungListe:
                db.session.delete(belegung)
                db.session.commit()
            schuelerListe_id = request.form.getlist('fach_schueler')
            for schueler_id in schuelerListe_id:
                belegung = Belegung(fach_id=fach_id, schueler_id=schueler_id)
                db.session.add(belegung)
                db.session.commit()

        flash(fach.bezeichnung + " wurde bearbeitet")

    if origin == "profile":
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('viewSubject', subject_id=fach_id))


@app.route('/profile/deleteSubject/<subject_id>', methods=['POST'])
@login_required
def deleteSubject(subject_id):
    fach = Fach.query.get_or_404(subject_id)
    db.session.delete(fach)
    db.session.commit()
    flash("Das Fach " + fach.bezeichnung + " wurde entfernt")
    return redirect(url_for('profile'))


@app.route('/profile/viewClass/<int:klasse_id>', methods=['GET', 'POST'])
def viewClass(klasse_id):
    klasse = Klasse.query.get_or_404(klasse_id)

    schuelerDerKlasse = Schueler.query.filter_by(klasse_id=klasse_id)

    belegungListe = Belegung.query.all()
    belegungenDerKlasse = []
    for schueler in schuelerDerKlasse:
        for belegung in belegungListe:
            if schueler.id == belegung.schueler_id:
                if belegung not in belegungenDerKlasse:
                    belegungenDerKlasse.append(belegung)

    faecherListe = Fach.query.all()
    faecherIDDerKlasse = []
    for belegung in belegungenDerKlasse:
        if belegung.fach_id not in faecherIDDerKlasse:
            faecherIDDerKlasse.append(belegung.fach_id)

    faecherDerKlasse = []
    for faecher_ID in faecherIDDerKlasse:
        fach = Fach.query.get_or_404(faecher_ID)
        if fach not in faecherDerKlasse:
            faecherDerKlasse.append(fach)

    pruefungListe = Pruefung.query.all()
    examenDerKlasse = []
    for pruefung in pruefungListe:
        for faecher in faecherDerKlasse:
            if faecher.id == pruefung.fach_id:
                examenDerKlasse.append(pruefung)

    schuelerList = Schueler.query.all()
    for s in schuelerList:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    notenschluesselListe = Notenschluessel.query.all()

    bewertungsListe = Bewertung.query.all()
    lehrerListe = Lehrer.query.all()
    for l in lehrerListe:
        l.vorname = decrypt(l.vorname)
        l.nachname = decrypt(l.nachname)
        l.email = decrypt(l.email)
    klassenListe = Klasse.query.all()

    origin = "class"

    return render_template("classDashboard.html", klasse=klasse, schuelerDerKlasse=schuelerDerKlasse,
                           faecherDerKlasse=faecherDerKlasse, examenDerKlasse=examenDerKlasse,
                           schuelerList=schuelerList, belegungListe=belegungListe, pruefungListe=pruefungListe,
                           faecherListe=faecherListe, bewertungsListe=bewertungsListe, lehrerListe=lehrerListe,
                           notenschluesselListe=notenschluesselListe, origin=origin, klassenListe=klassenListe
                           )


@app.route('/profile/viewSubject/<subject_id>', methods=['GET', 'POST'])
def viewSubject(subject_id):
    fach = Fach.query.get_or_404(subject_id)
    pruefungListe = Pruefung.query.all()
    belegungListe = Belegung.query.all()
    schuelerList = Schueler.query.all()
    for s in schuelerList:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    klassenListe = Klasse.query.all()

    pruefungenDesFaches = []
    for pruefung in pruefungListe:
        if pruefung.fach_id == fach.id:
            pruefungenDesFaches.append(pruefung)

    schuelerDesFaches = []
    for belegung in belegungListe:
        if belegung.fach_id == fach.id:
            for schueler in schuelerList:
                if schueler.id == belegung.schueler_id:
                    schuelerDesFaches.append(schueler)
                    
    klassenDesFaches = []
    for schueler in schuelerDesFaches:
        for klasse in klassenListe:
            if schueler.klasse_id == klasse.id:
                if klasse not in klassenDesFaches:
                    klassenDesFaches.append(klasse)

    notenschluesselListe = Notenschluessel.query.all()
    bewertungsListe = Bewertung.query.all()
    lehrerListe = Lehrer.query.all()
    for l in lehrerListe:
        l.vorname = decrypt(l.vorname)
        l.nachname = decrypt(l.nachname)
        l.email = decrypt(l.email)
    faecherListe = Fach.query.all()


    origin = "subject"

    return render_template("subjectDashboard.html", fach=fach, schuelerDesFaches=schuelerDesFaches,
                           klassenDesFaches=klassenDesFaches, pruefungenDesFaches=pruefungenDesFaches,
                           schuelerList=schuelerList, belegungListe=belegungListe, pruefungListe=pruefungListe,
                           faecherListe=faecherListe, bewertungsListe=bewertungsListe, lehrerListe=lehrerListe,
                           notenschluesselListe=notenschluesselListe, origin=origin, klassenListe=klassenListe)



@app.route('/profile/viewExam/<pruefung_id>', methods=['GET', 'POST'])
def viewExam(pruefung_id):
    pruefung = db.session.query(Pruefung).filter(Pruefung.id == pruefung_id).first()
    pruefungliste = Pruefung.query.all()
    schuelerDerPruefung = db.session.query(Pruefung, Schueler, Belegung).filter(
        Pruefung.fach_id == Belegung.fach_id).filter(Belegung.schueler_id == Schueler.id).filter(
        Pruefung.id == pruefung_id).all()
    bewertungDerPruefung = db.session.query(Pruefung, Bewertung).filter(Pruefung.id == Bewertung.pruefung_id).filter(
        Pruefung.id == pruefung_id).all()
    notenschluesselListe = db.session.query(Notenschluessel).filter(Notenschluessel.pruefung_id == pruefung_id)
    notenliste = list(notenschluesselListe)
    schuelerList = Schueler.query.all()
    for s in schuelerList:
        s.vorname = decrypt(s.vorname)
        s.nachname = decrypt(s.nachname)
    belegungListe = Belegung.query.all()
    faecherListe = Fach.query.all()
    bewertungsListe = Bewertung.query.all()

    labels = [1, 2, 3, 4, 5, 6]
    data = [0, 0, 0, 0, 0, 0]

    for bewertungen in bewertungDerPruefung:

        punkte = bewertungen.Bewertung.punkte
        for index, noten in enumerate(notenliste):

            if index == 5:
                data[index] += 1
                break

            if noten.punkte_obergrenze >= punkte > notenliste[index + 1].punkte_obergrenze:
                data[index] += 1
                break

    average = 0
    total = 0
    for index, element in enumerate(data):
        if element != 0:
            average += (index + 1) * element
            total += element
    average = round((average / total), 1)

    return render_template("examDashboard.html", pruefung=pruefung, pruefungListe=pruefungliste, schuelerList=schuelerList,
                           faecherListe=faecherListe,bewertungsListe=bewertungsListe, schuelerDerPruefung=schuelerDerPruefung,
                           belegungListe=belegungListe, bewertungDerPruefung=bewertungDerPruefung, notenschluesselListe=notenschluesselListe,
                           labels=labels, data=data, average=average)


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


class Notenschluessel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Integer, nullable=True)
    punkte_obergrenze = db.Column(db.Integer, nullable=True)
    pruefung_id = db.Column(db.Integer, nullable=True)


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
    pruefung_id = db.Column(db.Integer, primary_key=True)
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
    fach_id = db.Column(db.Integer, nullable=True)


app.run(debug=True)
