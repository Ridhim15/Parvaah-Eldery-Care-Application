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
# Configure the app for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admin@localhost/parvaah'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'

db = SQLAlchemy(app)
# -------------------- Session config --------------------
app.config['SESSION_TYPE']             = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY']       = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
Session(app)
# connection=mysql.connector.connect(host='localhost, user='root', password='', database='Parvaah')


class Elderly(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email    = db.Column(db.String(50), unique=True, nullable=False)
    image_url= db.Column(db.String(200))
    name     = db.Column(db.String(100))
    age      = db.Column(db.Integer)
    # gid      = db.Column(db.Integer)
    # guardian = db.relationship(Guardian, backref=db.backref('elderly', lazy=True))

    def __repr__(self):
        return f'<Elderly {self.username}>'
    
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
class Guardian(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    image_url= db.Column(db.String(200), nullable=False)
    name     = db.Column(db.String(100), nullable=False)
    age      = db.Column(db.Integer, nullable=False)
    eid      = db.Column(db.Integer , nullable=False)
    # elderly = db.relationship(Elderly, backref=db.backref('guardian', lazy=True))

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
    logged_in = 'username' in session
    if logged_in:
        username = session['username']
        current_user = Elderly.query.filter_by(username=username).first()
        return render_template('index.html', logged_in=logged_in, current_user=current_user)
    else:
        return render_template('index.html', logged_in=logged_in)
@app.route('/<user>')
def user(user):
    return render_template('login.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        elderly = Elderly.query.filter_by(username=username, password=password).first()

        if elderly:
            session['username'] = elderly.username
            session['user_id'] = elderly.id
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

# @app.route('/logout', methods=['POST'])
# def logout():
#     session.pop('username', None)
#     session.pop('user_id', None)
#     flash("You have been logged out.", "info")
#     return redirect(url_for('login'))



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
            return redirect(url_for('index'))
    return make_response('Invalid request method', 405)
        
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
    
@app.route('/test_db')
def test_db():
    try:
        # Use text() to perform a raw SQL query to check connection
        db.session.execute(text('SELECT 1'))
        return "Database is connected!"
    except Exception as e:
        return f"Error connecting to the database: {str(e)}"

# Route to add a test record to the database
@app.route('/add_test_data')
def add_test_data():
    try:
        # Create a new elderly record with image_url
        new_elderly = Elderly(
            username='testuser', 
            password='password123', 
            name='Test User', 
            email='test@gmail.com',
            age=70,
            image_url='https://example.com/testuser.jpg'  # Add a sample image URL
        )
        db.session.add(new_elderly)
        db.session.commit()
        return "Test data added successfully!"
    except Exception as e:
        return f"Error adding test data: {str(e)}"

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
    with app.app_context(): db.create_all()
    app.run(debug=True)
    
