from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests.models import Response


# from dotenv import load_dotenv
from functools import partial
from os import environ
from datetime import datetime
import json
import mysql.connector
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

# load_dotenv()

app = Flask(__name__)
api = Api(app)
# app.secret_key = environ['SECRET_KEY']
# load_dotenv()
# -------------------- Session and SQL config --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SESSION_TYPE']             = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY']       = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
Session(app)


# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Database Classes ----------------------------------
# -------------------------------------------------------------------------------------------------

class Elderly(db.Model):
    eid           = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(50), nullable=False)
    dob           = db.Column(db.Date)
    phone         = db.Column(db.String(15))
    profile_image = db.Column(db.String(200))
    # gid      = db.Column(db.Integer)
    # guardian = db.relationship(Guardian, backref=db.backref('elderly', lazy=True))
    
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Guardian(db.Model):
    gid           = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(50), nullable=False)
    dob           = db.Column(db.Date)
    phone         = db.Column(db.String(15))
    profile_image = db.Column(db.String(200))
    # elderly= db.relationship(Elderly, backref=db.backref('guardian', lazy=True))
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def check_password(self, password):
        return check_password_hash(self.password, password)
class Caretaker(db.Model):
    cid           = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(50), nullable=False)
    dob           = db.Column(db.Date)
    phone         = db.Column(db.String(15))
    profile_image = db.Column(db.String(200))
    # elderly= db.relationship(Elderly, backref=db.backref('guardian', lazy=True))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email    = email

    def check_password(self, password):
        return check_password_hash(self.password, password)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Google Auth ---------------------------------------
# -------------------------------------------------------------------------------------------------

# environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
# environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# blueprint = make_google_blueprint(
#     client_id     = environ['GOOGLE_CLIENT_ID'],
#     client_secret = environ['GOOGLE_CLIENT_SECRET'],
#     scope         = ['email','profile'],
#     offline       = True,
#     redirect_to   = 'google_auth'
# )
# app.register_blueprint(blueprint, url_prefix='/login')

# @app.route('/google_auth')
# def google_auth():
#     # get email and name from google
#     if not google.authorized:
#         return redirect(url_for('google.login'))
#     try:
#         resp = google.get('/oauth2/v2/userinfo')
#         assert resp.ok, resp.text
#         email = resp.json()['email']
#         name = resp.json()['name']
#         session['email'] = email
#         session['name']  = name
#         return redirect(url_for('dashboard'))
#     except TokenExpiredError:
#         return redirect(url_for('google.login'))

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Login -------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    logged_in = 'username' in session
    if logged_in:
        username = session['username']
        current_user = Elderly.query.filter_by(username=username).first()
        return render_template('dashboard.html', logged_in=logged_in, current_user=current_user)
    else:
        return render_template('index.html', logged_in=logged_in)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']

        user = Elderly.query.filter_by(username=username).first()
        if user:
            return make_response('User already exists', 400)
        else:
            session['username'] = username
            session['email'] = email
            new_user = Elderly(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            session['email'] = new_user.email
            session['profile_image'] = new_user.profile_image if new_user.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
            return redirect(url_for('dashboard'))
    return make_response('Invalid request method', 405)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        elderly = Elderly.query.filter_by(username=username, password=password).first()

        if elderly:
            session['username'] = elderly.username
            session['user_id'] = elderly.eid
            session['profile_image'] = elderly.profile_image if elderly.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))



# -------------------------------------------------------------------------------------------------
# --------------------------------------------- APIs ----------------------------------------------
# -------------------------------------------------------------------------------------------------

class login_status(Resource):
    def get(self):
        if 'username' in session:
            return {'status': 'logged_in', 'username': session['username'],'profile_image':session['profile_image']}
        else:
            return {'status': 'logged_out'}

api.add_resource(login_status, '/api/login_status')


# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes and Views ----------------------------------
# -------------------------------------------------------------------------------------------------

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

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/guardian')
def guardian():
    return render_template('guardian.html')

@app.route('/caretakerlogin')
def caretakerlogin():
    return render_template('caretakerlogin.html')

@app.route('/guardiandashboard')
def guardiandashboard():
    return render_template('guardiandashboard.html')

@app.route('/reminder')
def reminder():
    return render_template('reminder.html')

@app.route('/appointreminder')
def appointreminder():
    return render_template('appointreminder.html')

@app.route('/newservice')
def newservice():
    return render_template('newservice.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/caretakerprofile')
def caretakerprofile():
    return render_template('caretakerprofile.html')

@app.route('/dashservices')
def dashservices():
    return render_template('dashservices.html')

@app.route('/sos')
def sos():
    return render_template('sos.html')

@app.route('/caretakerdash')
def caretakerdash():
    return render_template('caretakerdash.html')

@app.route('/yourhealth')
def yourhealth():
    return render_template('yourhealth.html')




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

