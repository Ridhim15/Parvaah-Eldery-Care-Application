from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests.models import Response
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64


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
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    fare = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('elderly.eid'), nullable=False)

    def __init__(self, service_type, service_name, start_date, start_time, end_date, end_time, fare, user_id):
        self.service_type = service_type
        self.service_name = service_name
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.fare = fare
        self.user_id = user_id



class Elderly(db.Model):
    eid               = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(100))
    username          = db.Column(db.String(50), unique=True, nullable=False)
    email             = db.Column(db.String(50), unique=True, nullable=False)
    password          = db.Column(db.String(50), nullable=False)
    dob               = db.Column(db.Date)
    phone             = db.Column(db.Integer)
    profile_image     = db.Column(db.String(200), default='/static/assets/images/profile_def_m.png')
    address           = db.Column(db.String(500))
    emergency_contact = db.Column(db.Integer)
    bloodgroup        = db.Column(db.String(5))
    disease           = db.Column(db.String(200))
    allergy           = db.Column(db.String(200))
    form_filled = db.Column(db.Boolean, default=False)  # New column to track form submission
    # gid      = db.Column(db.Integer)
    # guardian = db.relationship(Guardian, backref=db.backref('elderly', lazy=True))
    
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class AppointmentReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('elderly.eid'), nullable=False)

    def __init__(self, title, location, time, date, user_id):
        self.title = title
        self.location = location
        self.time = time
        self.date = date
        self.user_id = user_id
        
@app.route('/appointreminder', methods=['GET', 'POST'])
def appointreminder():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = Elderly.query.filter_by(username=username).first()

    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        time = request.form['time']
        date = request.form['date']

        # Save the appointment reminder in the database
        new_appointment = AppointmentReminder(
            title=title,
            location=location,
            time=datetime.strptime(time, "%H:%M").time(),
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            user_id=user.eid
        )

        db.session.add(new_appointment)
        db.session.commit()

        flash('Appointment reminder added successfully!', 'success')
        return redirect(url_for('appointreminder'))

    # Fetch the appointments for the current user
    appointments = AppointmentReminder.query.filter_by(user_id=user.eid).all()
    return render_template('appointreminder.html', appointments=appointments)

class MedicineReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.Integer, nullable=False)  # Number of times to take the medicine
    times = db.Column(db.String(500), nullable=False)  # Store multiple times as a comma-separated string
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('elderly.eid'), nullable=False)

    def __init__(self, medicine_name, dosage, times, start_date, end_date, user_id):
        self.medicine_name = medicine_name
        self.dosage = dosage
        self.times = times
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id




class Guardian(db.Model):
    gid           = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(50), nullable=False)
    dob           = db.Column(db.Date)
    phone         = db.Column(db.String(15))
    profile_image = db.Column(db.String(200))
    address       = db.Column(db.String(500))
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
    address       = db.Column(db.String(500))
    specializatin = db.Column(db.String(200))
    job_title     = db.Column(db.String(200))
    # elderly= db.relationship(Elderly, backref=db.backref('guardian', lazy=True))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email    = email

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
# this is only for reference purposes do not delete it
# class Medical_record(db.Model):
#     mid = db.Column(db.Integer, nullable=False)
#     date = db.Column(db.Date)
#     sugar = db.Column(db.Integer)
#     bp_sys = db.Column(db.Integer)
#     bp_dia = db.Column(db.Integer)


    
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
        #fetching form data from the user
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']

        # Check if the username already exists
        existing_user = Elderly.query.filter_by(username=username).first()
        if existing_user:
            return redirect(url_for('login'))
        else:
            session['username'] = username
            session['email'] = email
            # Create a new user and save it to the database
            hashed_password = generate_password_hash(password)
            new_user = Elderly(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            session['email'] = new_user.email
            session['profile_image'] = new_user.profile_image if new_user.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
            
            return redirect(url_for('fill_form',user=new_user))
    return make_response('Invalid request method', 405)

# ------------------------------------ Form Route ----------------------------

@app.route('/form', methods=['GET','POST'])
@app.route('/fill_form', methods=['GET', 'POST'])
def fill_form():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the form data from the user
        username = session['username']
        diseases = request.form.getlist('diseases[]')  # Example for multiple selected diseases
        blood_type = request.form['bloodType']
        health_details = request.form['healthDetails']
        dob = request.form['dob']
        

        # Update the user's information in the Elderly table
        user = Elderly.query.filter_by(username=username).first()
        user.disease = ','.join(diseases)  # Store diseases as a comma-separated string
        user.bloodgroup = blood_type
        user.allergy = health_details
        user.form_filled = True  # Mark form as filled
        db.session.commit()

        # Create the health data table for this user
        create_user_health_table(username)

        # Redirect to the dashboard after form submission
        return redirect(url_for('dashboard'))

    user = Elderly.query.filter_by(username=session['username']).first()
    return render_template('form.html', user=user)

def create_user_health_table(username):
    """Dynamically create a table for each user to store their health records."""
    table_name = f"health_{username}"
    query = text(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, date DATE, sugar INTEGER, bp_sys INTEGER, bp_dia INTEGER)")
    db.session.execute(query)
    db.session.commit()





@app.route('/login', methods=['GET', 'POST'])
def login():
    print("LOGIN attempted")
    if request.method == 'POST':
        print('Huh, this is /login')
        username = request.form['username']
        password = request.form['password']
        
        user = Elderly.query.filter_by(username=username).first() or Elderly.query.filter_by(email=username).first()

        if user and check_password_hash(user.password, password):
            print('Username, pw is correct')
            session['username'] = user.username
            session['user_id'] = user.eid
            session['profile_image'] = user.profile_image

            # If the form has not been filled, redirect to the form page
            if not user.form_filled:
                return redirect(url_for('fill_form'))
            print(f'{session["username"]} logged in successfully')
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password'
    
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/test')
def test():
    print(session)
    return 'Logged in' if 'username' in session else 'Not logged in'



# -------------------------------------------------------------------------------------------------
# --------------------------------------------- APIs ----------------------------------------------
# -------------------------------------------------------------------------------------------------

class login_status(Resource):
    def get(self):
        if 'username' in session:
            return {'status': 'logged_in', 'username': session['username'],'profile_image':session.get('profile_image')}
        else:
            return {'status': 'logged_out'}

api.add_resource(login_status, '/api/login_status')


# -------------------------------------------------------------------------------------------------
# ------------------------------------------- Sugar and BP Graph ----------------------------------
# -------------------------------------------------------------------------------------------------

# @app.route('/insights')
# def insights():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     username = session['username']
#     table_name = f"health_{username}"
    
#     # Fetch the health data for the last month
#     query = f"SELECT * FROM {table_name} WHERE date >= datetime('now', '-30 days')"
#     results = db.session.execute(query).fetchall()

#     dates = [row['date'] for row in results]
#     sugar_levels = [row['sugar'] for row in results]
#     bp_sys = [row['bp_sys'] for row in results]
#     bp_dia = [row['bp_dia'] for row in results]

#     # Create the graphs
#     sugar_graph = create_line_graph(dates, sugar_levels, "Sugar Levels")
#     bp_graph = create_line_graph(dates, bp_sys, "BP Systolic", bp_dia, "BP Diastolic")

#     return render_template('insights.html', sugar_graph=sugar_graph, bp_graph=bp_graph)

# def create_line_graph(dates, data1, label1, data2=None, label2=None):
#     """Helper function to create a base64-encoded image for a line graph."""
#     plt.figure()
#     plt.plot(dates, data1, label=label1, color='blue')
#     if data2:
#         plt.plot(dates, data2, label=label2, color='red')
#     plt.xticks(rotation=45)
#     plt.legend()
#     plt.tight_layout()

#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graph_url = base64.b64encode(img.getvalue()).decode('utf8')
#     plt.close()  # Close the figure after saving it

#     return 'data:image/png;base64,{}'.format(graph_url)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes and Views ----------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = Elderly.query.filter_by(username=username).first()

    # Fetch upcoming appointments and medicine reminders for the logged-in user
    upcoming_appointments = AppointmentReminder.query.filter_by(user_id=user.eid).all()
    upcoming_reminders = MedicineReminder.query.filter_by(user_id=user.eid).all()

    return render_template('dashboard.html', user=user, upcoming_appointments=upcoming_appointments, upcoming_reminders=upcoming_reminders)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user=Elderly.query.filter_by(username=session['username']).first()
    health = db.session.execute(text(f"SELECT * FROM health_{user.username}")).fetchall()

    return render_template('profile.html', user=user, health=health)

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

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = Elderly.query.filter_by(username=username).first()

    if request.method == 'POST':
        service_type = request.form['type']
        service_name = request.form['service']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        # Convert time and date into datetime objects to calculate the fare
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

        if end_datetime <= start_datetime:
            flash('End time must be later than start time.', 'danger')
            return redirect(url_for('booking'))

        # Calculate the difference in hours and the fare (₹200 per hour as an example)
        time_difference = (end_datetime - start_datetime).total_seconds() / 3600
        fare = time_difference * 200

        # Save the booking in the database
        new_booking = Booking(
            service_type=service_type,
            service_name=service_name,
            start_date=start_datetime.date(),
            start_time=start_datetime.time(),
            end_date=end_datetime.date(),
            end_time=end_datetime.time(),
            fare=fare,
            user_id=user.eid
        )

        db.session.add(new_booking)
        db.session.commit()

        flash('Service booked successfully!', 'success')
        return redirect(url_for('thanks'))

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

@app.route('/guardian')
def guardian():
    return render_template('guardian.html')

@app.route('/caretakerlogin')
def caretakerlogin():
    return render_template('caretakerlogin.html')

@app.route('/guardiandashboard')
def guardiandashboard():
    return render_template('guardiandashboard.html')

@app.route('/reminder', methods=['GET', 'POST'])
def medicinereminder():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = Elderly.query.filter_by(username=username).first()

    if request.method == 'POST':
        medicine_name = request.form['medicine_name']
        dosage = int(request.form['dosage'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Collect all the times (depending on dosage)
        times = [request.form[f'time_{i}'] for i in range(1, dosage + 1)]
        times_str = ','.join(times)  # Store times as a comma-separated string

        # Save the medicine reminder in the database
        new_medicine_reminder = MedicineReminder(
            medicine_name=medicine_name,
            dosage=dosage,
            times=times_str,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            user_id=user.eid
        )

        db.session.add(new_medicine_reminder)
        db.session.commit()

        flash('Medicine reminder added successfully!', 'success')
        return redirect(url_for('medicinereminder'))

    # Fetch the medicine reminders for the current user
    medicine_reminders = MedicineReminder.query.filter_by(user_id=user.eid).all()
    return render_template('reminder.html', medicine_reminders=medicine_reminders)



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

