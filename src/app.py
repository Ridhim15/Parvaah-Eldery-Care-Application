from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory,flash
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests.models import Response
from dotenv import load_dotenv
from os import environ
from datetime import datetime
import json
import mysql.connector


load_dotenv()
app = Flask(__name__)
api = Api(app)
app.secret_key = environ['SECRET_KEY']

# connection=mysql.connector.connect(host='localhost, user='root', password='', database='Parvaah')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
db = SQLAlchemy(app)

class Elderly(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    image_url= db.Column(db.String(200), nullable=False)
    name     = db.Column(db.String(100), nullable=False)
    age      = db.Column(db.Integer, nullable=False)
    g_id     = db.Column(db.Integer, db.ForeignKey(Guardian.id), nullable=False)
    guardian = db.relationship(Guardian, backref=db.backref('elderly', lazy=True))



environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # ONLY ON LOCAL ENV
blueprint = make_google_blueprint(
    client_id     = environ['GOOGLE_CLIENT_ID'],
    client_secret = environ['GOOGLE_CLIENT_SECRET'],
    scope         = ['email','profile'],
    offline       = True,
    redirect_to   = 'google_auth'
)
app.register_blueprint(blueprint, url_prefix='/login')


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/<user>')
def user(user):
    return render_template('login.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        elderly = Elderly.query.filter_by(username=username, password=password).first()

        if ngo:
            session['username'] = ngo.username
            session['user_id'] = ngo.id
            return redirect(url_for('ngo', id=ngo.id))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']

        existing_user = NGO.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        new_user = NGO(username=username, password=password, phone=phone, address=address, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered Successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/google_auth')
def google_auth():
    # get email and name from google
    if not google.authorized:
        return redirect(url_for('google.login'))
    try:
        resp = google.get('/oauth2/v2/userinfo')
        assert resp.ok, resp.text
        email = resp.json()['email']
        name = resp.json()['name']
        session['email'] = email
        session['name'] = name
        return redirect(url_for('dashboard'))
    except TokenExpiredError:
        return redirect(url_for('google.login'))
    


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/homecare')
def homecare():
    return render_template('homecare.html')

@app.route('/medicalcare')
def medicalcare():
    return render_template('medicalcare.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/community')
def community():
    return render_template('community.html')


if __name__ == '__main__':
    app.run(debug=True)
