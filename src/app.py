from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory
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

load_dotenv()
app = Flask(__name__)
api = Api(app)

# app.secret_key = environ['SECRET_KEY']
# app.config['SESSION_TYPE'] = ''

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
    

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

@app.route('/user')
def user():
    return render_template('user.html')

if __name__ == '__main__':
    app.run(debug=True)

