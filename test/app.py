from flask import Flask, render_template, redirect, url_for, session, request, flash,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import environ

load_dotenv()

app = Flask(__name__)
app.secret_key = environ['SECRET_KEY']

# -------------------- Session config --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

# -------------------- Database Model --------------------
class Elderly(db.Model):
    eid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email

    def check_password(self, password):
        return check_password_hash(self.password, password)

# -------------------- Routes --------------------
@app.route('/')
def index():
    logged_in = 'username' in session
    if logged_in:
        username = session['username']
        current_user = Elderly.query.filter_by(username=username).first()
        return render_template('index.html', logged_in=logged_in, current_user=current_user)
    else:
        return render_template('index.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        elderly = Elderly.query.filter_by(username=username).first()

        if elderly and elderly.check_password(password):
            session['username'] = elderly.username
            session['user_id'] = elderly.eid
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']  # Add this line to get the name from the form

        user = Elderly.query.filter_by(username=username).first()
        if user:
            return make_response('User already exists', 400)
        else:
            session['username'] = username
            session['email'] = email
            new_user = Elderly(username=username, password=password, email=email, name=name)  # Pass the name to the constructor
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
    return make_response('Invalid request method', 405)

@app.route('/homecare')
def homecare():
    return render_template('homecare.html')

@app.route('/medicalcare')
def medicalcare():
    return render_template('medicalcare.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/community')
def community():
    return render_template('community.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
