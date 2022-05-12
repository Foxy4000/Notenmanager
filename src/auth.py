from flask import Blueprint, render_template, session, request, app

#from . import db

auth = Blueprint('auth', __name__)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template("index.html")

#@auth.route('/signup')
#def signup():
 #   return 'Signup'
