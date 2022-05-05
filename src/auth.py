from flask import Blueprint, render_template, session
#from . import db

auth = Blueprint('auth', __name__)

@auth.route("/login")
def login():
    # session['logged_in'] = False erst wenn der Button geklickt wird (Funktion noch nicht implementiert)
    session['logged_in'] = True
    return render_template("login.html")


#@auth.route('/signup')
#def signup():
 #   return 'Signup'

@auth.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template("profile.html")
