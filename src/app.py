# -*- coding: utf-8 -*-
from flask import Flask, render_template, Blueprint, session
#from . import db

#Create a Flask Instance
app = Flask(__name__)
main = Blueprint('main', __name__)
app.secret_key = "secret key"


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
    return render_template("profile.html")

@app.route("/profile", methods = ['POST'])
def profile():
    return render_template("profile.html")



app.run(debug=True)