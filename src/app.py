import email
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
from datetime import datetime, timedelta
import json
import mysql.connector
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

# Import models from models.py

from models import AppointmentReminder, HealthInfo, db, User, GuardianElderly, Booking, MedicineReminder, Caretaker, UserRole, BookingStatus


# load_dotenv()

app = Flask(__name__)
api = Api(app)
# app.secret_key = environ['SECRET_KEY']
# load_dotenv()
# -------------------- Session and SQL config --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['SESSION_TYPE']             = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY']       = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
Session(app)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Login -------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    logged_in = 'email' in session
    if logged_in:
        email = session['email']
        current_user = User.query.filter_by(email=email).first()
        return render_template('dashboard.html', logged_in=logged_in, current_user=current_user)
    else:
        return render_template('index.html', logged_in=logged_in)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        #fetching form data from the user
        full_name = request.form['full_name']
        password = request.form['password']
        email    = request.form['email']
        print(f'full_name: {full_name}, password: {password}, email: {email}')
        # Check if the username already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return redirect(url_for('login'))
        else:
            session['username'] = full_name
            session['email'] = email
            # Create a new user and save it to the database
            hashed_password = generate_password_hash(password)
            new_user = User(full_name=full_name, password=hashed_password, email=email, role=UserRole.elderly)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.full_name
            session['email'] = new_user.email
            session['profile_image'] = new_user.profile_image if new_user.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
            
            return redirect(url_for('fill_form', user=new_user))
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
        blood_type = request.form['blood_type']
        additional_health_details = request.form['additional_health_details']
        dob = request.form['dob']
        

        # Update the user's information in the User table
        user = User.query.filter_by(full_name=username).first()
        user.disease = ','.join(diseases)  # Store diseases as a comma-separated string
        user.blood_type = blood_type
        user.additional_health_details = additional_health_details
        user.dob = datetime.strptime(dob, "%Y-%m-%d").date()
        db.session.commit()

        # Create the health data table for this user
        # create_user_health_table(username)

        # Redirect to the dashboard after form submission
        return redirect(url_for('dashboard'))

    user = User.query.filter_by(full_name=session['username']).first()
    return render_template('form.html', user=user)

# def create_user_health_table(username):
#     """Dynamically create a table for each user to store their health records."""
#     table_name = f"health_{username}"
#     query = text(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, date DATE, sugar INTEGER, bp_sys INTEGER, bp_dia INTEGER)")
#     db.session.execute(query)
#     db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("LOGIN attempted")
    if request.method == 'POST':
        print('Huh, this is /login')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(full_name=username).first() or User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            print('Username, pw is correct')
            session['username'] = user.full_name
            session['user_id'] = user.user_id
            session['profile_image'] = user.profile_image
            session['email'] = user.email
            # If the form has not been filled, redirect to the form page
            if not user.disease or not user.blood_type or not user.additional_health_details:
                return redirect(url_for('fill_form'))
            print(f'{session["username"]} logged in successfully')
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password'
    
    return render_template('login.html')

@app.route('/login_guardian', methods=['GET', 'POST'])
def login_guardian():
    print("Guardian LOGIN attempted")
    if request.method == 'POST':
        print('Huh, this is /login_guardian')
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, role=UserRole.guardian).first()
        
        if user and check_password_hash(user.password, password):
            print('Guardian email and password are correct')
            session['email'] = user.email
            session['role'] = 'guardian'
            session['username'] = user.full_name
            session['user_id'] = user.user_id
            session['profile_image'] = user.profile_image
            
            # Redirect to guardian-specific dashboard
            print(f'{session["username"]} logged in successfully as guardian')
            return redirect(url_for('dashboard_guardian'))
        else:
            flash('Invalid email or password')
            print('Invalid email or password for guardian')
    
    return render_template('login_guardian.html')

# Caretaker Login
@app.route('/login_caretaker', methods=['GET', 'POST'])
def login_caretaker():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        caretaker = Caretaker.query.filter_by(email=email).first()
        
        if caretaker and check_password_hash(caretaker.password, password):
            session['username'] = caretaker.full_name
            session['caretaker_id'] = caretaker.caretaker_id
            session['email'] = caretaker.email
            session['role'] = 'caretaker'
            
            # Redirect to caretaker-specific dashboard
            return redirect(url_for('caretaker_dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login_caretaker.html')



@app.route('/logout', methods=['GET'])
def logout():
    print(f'{session["username"]} logged out successfully')
    print(f"{session['email']}: session['email']")
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
    user = User.query.filter_by(full_name=username).first()

    # Fetch initial upcoming appointments and medicine reminders for the logged-in user
    upcoming_appointments = AppointmentReminder.query.filter_by(user_id=user.user_id).all()
    upcoming_reminders = MedicineReminder.query.filter_by(user_id=user.user_id).all()

    return render_template('dashboard.html', user=user, 
                           upcoming_appointments=upcoming_appointments, 
                           upcoming_reminders=upcoming_reminders)
# @app.route('/profile')
# def profile():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     user = User.query.filter_by(full_name=session['username']).first()
#     # health = db.session.execute(text(f"SELECT * FROM health_{user.full_name}")).fetchall()

#     return render_template('profile.html', user=user, health=health)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(full_name=session['username']).first()
    health = db.session.execute(text(f"SELECT * FROM health_info")).fetchall()

    return render_template('profile.html', user=user, health=health)

    
#     # Fetch the elderly user based on the session username (full_name assumed unique for now)
#     elderly_user = User.query.filter_by(full_name=session['username']).first()
    
#     if not elderly_user:
#         return "User not found.", 404

#     # Fetch guardian(s) using the email as the linking key
#     guardian_relations = GuardianElderly.query.filter_by(elderly_id=elderly_user.email).all()
#     guardians = [User.query.filter_by(email=relation.guardian_id).first() for relation in guardian_relations]

#     return render_template('profile.html', user=elderly_user, guardians=guardians)


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
    user = User.query.filter_by(full_name=username).first()

    if request.method == 'POST':
        # Retrieve form data
        type_of_service = request.form.get('type')
        service = request.form.get('service')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')

        # Ensure date and time values are provided
        if not all([start_date, start_time, end_date, end_time]):
            flash("Please fill out all date and time fields.", "error")
            return redirect(url_for('booking'))

        # Convert date and time inputs into datetime objects
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

        # Create a new booking instance
        new_booking = Booking(
            user_id=user.user_id,
            type_of_service=type_of_service,
            service=service,
            start_date=start_datetime.date(),
            start_time=start_datetime.time(),
            end_date=end_datetime.date(),
            end_time=end_datetime.time(),
            status=BookingStatus.pending  # Default status
        )

        # Add and commit the new booking to the database
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


@app.route('/register_guardian', methods=['GET', 'POST'])
def register_guardian():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        elderly_email = request.form['elderly_email']

        # Check if elderly with provided email exists
        elderly = User.query.filter_by(email=elderly_email, role=UserRole.elderly).first()
        if not elderly:
            print("Elderly email not found. Please verify.")
            flash("Elderly email not found. Please verify.")
            return redirect(url_for('register_guardian'))

        # Check if guardian already exists
        if User.query.filter_by(email=email).first():
            print("Guardian Email already registered.")
            flash("Guardian Email already registered.")
            return redirect(url_for('register_guardian'))

        # Create new guardian user
        new_guardian = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role=UserRole.guardian
        )
        db.session.add(new_guardian)
        db.session.commit()

        # Link the new guardian to the existing elderly user
        guardian_elderly_link = GuardianElderly(
            guardian_email=email,
            elderly_email=elderly_email
        )
        db.session.add(guardian_elderly_link)
        db.session.commit()

        flash("Registration successful. Redirecting to dashboard.")
        return redirect(url_for('dashboard_guardian'))

    return render_template('register_guardian.html')

@app.route('/dashboard_guardian')
def dashboard_guardian():
    return render_template('dashboard_guardian.html')

@app.route('/reminder', methods=['GET', 'POST'])
def medicinereminder():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(full_name=username).first()

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
            user_id=user.user_id
        )

        db.session.add(new_medicine_reminder)
        db.session.commit()

        flash('Medicine reminder added successfully!', 'success')
        return redirect(url_for('medicinereminder'))

    # Fetch the medicine reminders for the current user
    medicine_reminders = MedicineReminder.query.filter_by(user_id=user.user_id).all()
    return render_template('reminder.html', medicine_reminders=medicine_reminders)

 

@app.route('/appointreminder', methods=['GET', 'POST'])
def appointreminder():
    # Ensure the user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        # Retrieve form data
        appointment_name = request.form['title']
        location = request.form['location']
        time = request.form['time']
        date = request.form['date']

        # Save the appointment reminder in the database
        new_appointment_reminder = AppointmentReminder(
            appointment_name=appointment_name,
            location=location,
            time=datetime.strptime(time, "%H:%M").time(),
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            user_id=user.user_id
        )

        db.session.add(new_appointment_reminder)
        db.session.commit()

        flash('Appointment reminder added successfully!', 'success')
        return redirect(url_for('appointreminder'))

    # Fetch the appointment reminders for the current user
    appointment_reminders = AppointmentReminder.query.filter_by(user_id=user.user_id).all()
    return render_template('appointreminder.html', appointments=appointment_reminders)


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



@app.route('/yourhealth', methods=['GET', 'POST'])
def yourhealth():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = User.query.filter_by(full_name=username).first()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'blood_pressure':
            # Handle blood pressure form submission
            bp_date = request.form.get('bpDate')
            systolic = request.form.get('systol')
            diastolic = request.form.get('dystol')
            pulse = request.form.get('pulse')

            if all([bp_date, systolic, diastolic, pulse]):
                health_info = HealthInfo(
                    user_id=user.user_id,
                    bp_date=datetime.strptime(bp_date, "%Y-%m-%d").date(),
                    systolic=int(systolic),
                    diastolic=int(diastolic),
                    pulse=int(pulse),
                )
                db.session.add(health_info)
                db.session.commit()
                flash('Blood pressure information submitted successfully!', 'success')
            else:
                flash('Please fill out all fields for blood pressure.', 'error')

        elif form_type == 'sugar_level':
            # Handle sugar level form submission
            sugar_date = request.form.get('sugarDate')
            sugar_level = request.form.get('sugarLevel')

            if all([sugar_date, sugar_level]):
                health_info = HealthInfo(
                    user_id=user.user_id,
                    sugar_date=datetime.strptime(sugar_date, "%Y-%m-%d").date(),
                    sugar_level=int(sugar_level)
                )
                db.session.add(health_info)
                db.session.commit()
                flash('Sugar level information submitted successfully!', 'success')
            else:
                flash('Please fill out all fields for sugar level.', 'error')

        return redirect(url_for('yourhealth'))
    return render_template('yourhealth.html')

# Route to create sample data
@app.route('/create_sample_data')
def create_sample_data():
    # Create elderly user
    elderly_user = User(
        full_name="Ridhim",
        email="ridhim@gmail.com",
        password=generate_password_hash("1234"),
        role=UserRole.elderly,
        gender="male",
        dob=datetime.strptime("1950-01-01", "%Y-%m-%d").date(),
        phone_no="1234567890",
        address="123 Elderly St",
        disease="Artherites",
        blood_type="O+",
        additional_health_details="Needs regular checkups"
    )

    # Create guardian user
    guardian_user = User(
        full_name="Yash",
        email="yash@gmail.com",
        password=generate_password_hash("password"),
        role=UserRole.guardian,
        gender="female",
        dob=datetime.strptime("1980-01-01", "%Y-%m-%d").date(),
        phone_no="9876543211",
        address="456 Guardian St"
    )

    # Add users to the session
    db.session.add(elderly_user)
    db.session.add(guardian_user)
    db.session.commit()

    # Create guardian-elderly relationship
    guardian_elderly = GuardianElderly(
        guardian_id=guardian_user.user_id,
        elderly_id=elderly_user.user_id
    )
    db.session.add(guardian_elderly)
    db.session.commit()

    # Create sample medicine reminder
    medicine_reminder = MedicineReminder(
        medicine_name="Aspirin",
        dosage=2,
        times="08:00,20:00",
        start_date=datetime.now().date(),
        end_date=(datetime.now() + timedelta(days=30)).date(),
        user_id=elderly_user.user_id
    )
    db.session.add(medicine_reminder)

    # Create sample booking
    booking = Booking(
        user_id=elderly_user.user_id,
        service="Doctor Appointment",
        date=datetime.now() + timedelta(days=7),
        status=BookingStatus.pending
    )
    db.session.add(booking)

    # Commit all changes
    db.session.commit()

    return "Sample data created successfully!"


@app.route('/refresh-upcoming')
def refresh_upcoming():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Fetch user info
    user = User.query.filter_by(full_name=session['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Fetch upcoming appointments and medicine reminders
    upcoming_appointments = AppointmentReminder.query.filter_by(user_id=user.user_id).all()
    upcoming_reminders = MedicineReminder.query.filter_by(user_id=user.user_id).all()

    # Render the partial template with updated data
    return render_template('upcoming_section.html', 
                           upcoming_appointments=upcoming_appointments, 
                           upcoming_reminders=upcoming_reminders)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # create_sample_data()  # Uncomment to create sample data before running the app
    app.run(debug=True)
