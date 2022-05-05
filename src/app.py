# -*- coding: utf-8 -*-
from flask import Flask, render_template, Blueprint
#from . import db

#Create a Flask Instance
app = Flask(__name__)
main = Blueprint('main', __name__)


#Create a route decorator
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/profile/", subdomain ='addstudent')
def addstudent():
    return render_template("addstudent.html")


@app.route("/profile", methods = ['POST'])
def profile():
    return render_template("profile.html")



app.run(debug=True)