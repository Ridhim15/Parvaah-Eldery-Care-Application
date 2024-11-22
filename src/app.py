import atexit
import shutil
import os
import email
from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests.models import Response
import io
import base64

from functools import partial
from os import environ
from datetime import datetime, timedelta
import json
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

from models import AppointmentReminder, db, User, GuardianElderly, Booking, MedicineReminder, Caretaker, UserRole, BookingStatus

app = Flask(__name__)
api = Api(app)

# -------------------- Session and SQL config --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
Session(app)



# -------------------------------------------------------------------------------------------------
# ---------------------------------------- Helper Functions ---------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/suggest', methods=['POST'])
def suggest():
    query = request.form.get('query', '').lower()
    suggestions = User.query.filter(User.email.like(f"%{query}%")).all()
    return jsonify([{'email': s.email, 'address': s.address, 'phone': s.phone} for s in suggestions])


@app.route('/create_sample_user')
def create_sample_user():
    try:
        # Define sample user details
        full_name = "Ridhim"
        password = "1234"
        email = "ridhim@gmail.com"
        
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("\n\n THE SAMPLE USER ALREADY EXISTS\n\n")
            return jsonify({'message': 'Sample user already exists'}), 200
        
        # Create a new user and save it to the database
        hashed_password = generate_password_hash(password)
        new_user = User(full_name=full_name, password=hashed_password, email=email, role=UserRole.elderly)
        db.session.add(new_user)
        db.session.commit()
        
        print(f'Sample user created: {new_user}')
        return jsonify({'message': 'Sample user created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_sample_booking')
def create_sample_booking():
    try:
        # Define sample booking details
        user_emails = ["rushil@gmail.com", "arpit@gmail.com", "keshav@gmail.com"]
        service = "Home Care"
        status = BookingStatus.pending
        latitude = "28.7041"
        longitude = "77.1025"

        for user_email in user_emails:
            # Check if the user exists
            user = User.query.filter_by(email=user_email).first()
            if not user:
                # Create a new user if not exists
                user = User(
                    full_name=user_email.split('@')[0].capitalize(),
                    email=user_email,
                    password=generate_password_hash("samplepassword"),
                    role=UserRole.elderly
                )
                db.session.add(user)
                db.session.commit()
                print(f'New user created: {user_email}')

            # Create a new booking and save it to the database
            new_booking = Booking(
                user_email=user_email,
                service=service,
                status=status,
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(new_booking)
            print(f'Sample booking created for: {user_email}')

        db.session.commit()
        return jsonify({'message': 'Sample bookings created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Index ---------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    logged_in = 'email' in session
    if logged_in:
        email = session['email']
        current_user = User.query.filter_by(email=email).first()
        return render_template('dashboards/dashboard.html', logged_in=logged_in, current_user=current_user)
    else:
        return render_template('routes/index.html', logged_in=logged_in)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Register ------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    print("\n\n REGISTERING THE USER NOW \n\n\n")

    if request.method == 'POST':
        # Fetching form data from the user
        full_name = request.form['full_name']
        password = request.form['password']
        email = request.form['email']
        print(f'full_name: {full_name}, password: {password}, email: {email}')
        # Check if the username already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("\n\n THE USER ALREADY EXISTS\n\n")
            return redirect(url_for('login'))
        else:
            session['username'] = full_name
            session['email'] = email
            # Create a new user and save it to the database
            hashed_password = generate_password_hash(password)
            new_user = User(full_name=full_name, password=hashed_password, email=email, role=UserRole.elderly)
            print(f'FROM REGISTER ROUTE \n new_user: {new_user}')
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.full_name
            session['email'] = new_user.email
            session['role'] = new_user.role.value
            session['profile_image'] = new_user.profile_image if new_user.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
            print("\n\n Session updated successfully\n\n")
            print("Session data: ", session, "\n\n")

            print("-" * 30, "\n\n")
            return redirect(url_for('form'))
    return make_response('Invalid request method', 405)

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
            return redirect(url_for('login'))

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
        # Add the guardian to the session
        session['email'] = new_guardian.email
        session['role'] = new_guardian.role.value
        session['username'] = new_guardian.full_name
        session['profile_image'] = new_guardian.profile_image
        print(f"Session data: {session}")

        # Link the new guardian to the existing elderly user
        guardian_elderly_link = GuardianElderly(
            guardian_email=email,
            elderly_email=elderly_email
        )
        db.session.add(guardian_elderly_link)
        db.session.commit()
        print(f"Guardian {full_name} registered successfully and linked with elderly.")
        flash("Registration successful. Redirecting to dashboard.")
        return redirect(url_for('dashboard_guardian'))
    return render_template('logins/login_guardian.html')


@app.route('/register_caretaker', methods=['GET', 'POST'])
def register_caretaker():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the caretaker already exists
        caretaker = Caretaker.query.filter_by(email=email).first()
        if caretaker:
            flash('Caretaker already exists. Please login.')
            return redirect(url_for('login_caretaker'))
        
        # Create a new caretaker and save it to the database
        new_caretaker = Caretaker(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_caretaker)
        db.session.commit()
        
        # Add the caretaker to the session
        session['username'] = new_caretaker.full_name
        session['email'] = new_caretaker.email
        session['role'] = 'caretaker'
        
        return redirect(url_for('dashboard_caretaker'))
    return render_template('logins/login_caretaker.html')

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Forms ---------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/form', methods=['GET', 'POST'])
@app.route('/fill_form', methods=['GET', 'POST'])
def form():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Fetch form data
        email = session['email']
        full_name = request.form['full_name']
        gender = request.form['gender']
        address = request.form['address']
        dob = request.form['dob']
        phone_no = request.form['phone_no']
        blood_type = request.form['blood_type']
        diseases_list = request.form.getlist('diseases[]')
        diseases = ','.join(disease for disease in diseases_list[1:] if disease)
        additional_health_details = request.form['additional_health_details']
        guardian_email = request.form['guardian_email']
        guardian_name = request.form['guardian_name']
        guardian_address = request.form['guardian_address']
        guardian_contact = request.form['guardian_contact']

        # Check if the user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            # Update existing user
            user.full_name = full_name
            user.gender = gender
            user.address = address
            user.dob = datetime.strptime(dob, "%Y-%m-%d").date()
            user.phone_no = phone_no
            user.blood_type = blood_type
            user.diseases = diseases
            user.additional_health_details = additional_health_details
            user.guardian_email = guardian_email
            user.guardian_name = guardian_name
            user.guardian_address = guardian_address
            user.guardian_contact = guardian_contact
        
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('dashboard'))
    user = User.query.filter_by(email=session['email']).first()
    
    return render_template('forms/form.html', user=user)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Logins --------------------------------------------
# -------------------------------------------------------------------------------------------------

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
            session['profile_image'] = user.profile_image
            session['email'] = user.email
            session['role'] = user.role.value  # Set the role in the session
            # If the form has not been filled, redirect to the form page
            if not user.diseases or not user.blood_type:
                return redirect(url_for('form'))
            print(f'{session["username"]} logged in successfully')
            return redirect(url_for('dashboard'))
        elif user:
            return 'Invalid username or password'
        else:
            return 'You are not registered yet. Please register first'
    
    return render_template('logins/login.html')

@app.route('/login_guardian', methods=['GET', 'POST'])
def login_guardian():
    print("Guardian LOGIN attempted")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, role=UserRole.guardian).first()
        
        if user and check_password_hash(user.password, password):
            print('Guardian email and password are correct')
            session['email'] = user.email
            session['role'] = user.role.value  # Set the role in the session
            session['username'] = user.full_name
            session['profile_image'] = user.profile_image
            
            # Redirect to guardian-specific dashboard
            print(f'{session["username"]} logged in successfully as guardian')
            return redirect(url_for('dashboard_guardian'))
        else:
            flash('Invalid email or password')
            print('Invalid email or password for guardian')
    
    return render_template('logins/login_guardian.html')

# Caretaker Login
@app.route('/login_caretaker', methods=['GET', 'POST'])
def login_caretaker():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        caretaker = Caretaker.query.filter_by(email=email).first()
        
        if caretaker and check_password_hash(caretaker.password, password):
            session['username'] = caretaker.full_name
            session['email'] = caretaker.email
            session['role'] = 'caretaker'
            
            # Redirect to caretaker-specific dashboard
            return redirect(url_for('dashboard_caretaker'))
        else:
            flash('Invalid email or password')
    
    return render_template('logins/login_caretaker.html')

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Logout --------------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/logout', methods=['GET'])
def logout():
    print(f'{session["username"]} logged out successfully')
    print(f"{session['email']}: session['email']")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- APIs ----------------------------------------------
# -------------------------------------------------------------------------------------------------

class login_status(Resource):
    def get(self):
        if 'email' in session:
            return {
                'status': 'logged_in',
                'username': session['username'],
                'profile_image': session.get('profile_image'),
                'role': session.get('role')
            }
        else:
            return {'status': 'logged_out'}

api.add_resource(login_status, '/api/login_status')

@app.route('/api/bookings', methods=['GET', 'POST'])
def handle_bookings():
    if request.method == 'GET':
        return fetch_bookings()
    elif request.method == 'POST':
        return update_booking_status()

def fetch_bookings():
    try:
        # Fetch all bookings from the Booking table
        bookings = Booking.query.all()
        
        # Convert the bookings to a list of dictionaries
        bookings_list = []
        for booking in bookings:
            bookings_list.append({
                'id': booking.booking_id,
                'user_email': booking.user_email,
                'caretaker_email': booking.caretaker_email,
                'service': booking.service,
                'booking_date': booking.booking_date,
                'status': booking.status.name,  # Convert enum to string
                # Add other fields as needed
            })
        
        return jsonify(bookings_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_booking_status():
    try:
        booking_id = request.json.get('booking_id')
        new_status = request.json.get('status')
        caretaker_email = request.json.get('caretaker_email')

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        if new_status not in BookingStatus.__members__:
            return jsonify({'error': 'Invalid status'}), 400

        if new_status == 'accepted':
            caretaker = Caretaker.query.filter_by(email=caretaker_email).first()
            if not caretaker:
                return jsonify({'error': 'Caretaker not found'}), 404
            booking.caretaker_email = caretaker_email
        booking.status = BookingStatus[new_status]
        db.session.commit()

        return jsonify({'message': f'Booking {new_status} successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_booking_status', methods=['POST'])
def update_booking_status():
    try:
        user_email = request.json.get('user_email')
        new_status = request.json.get('new_status')
        caretaker_email = request.json.get('caretaker_email')

        booking = Booking.query.filter_by(user_email=user_email).first()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        if new_status not in BookingStatus.__members__:
            return jsonify({'error': 'Invalid status'}), 400

        if new_status == 'accepted':
            caretaker = Caretaker.query.filter_by(email=caretaker_email).first()
            print(f"Caretaker : {caretaker}")
            if not caretaker:
                print("\nCaretaker not found\n")
                return jsonify({'error': 'Caretaker not found'}), 404
            booking.caretaker_email = caretaker_email

        booking.status = BookingStatus[new_status]
        db.session.commit()

        return jsonify({'message': f'Booking {new_status} successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#make api for above update_booking_status
# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Dashboards ----------------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        print('Username not in session')
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

    # Fetch upcoming appointments and medicine reminders for the logged-in user
    upcoming_appointments = AppointmentReminder.query.filter_by(user_email=user.email).all()
    upcoming_reminders = MedicineReminder.query.filter_by(user_email=user.email).all()

    return render_template('dashboards/dashboard.html', user=user, upcoming_appointments=upcoming_appointments, upcoming_reminders=upcoming_reminders)

@app.route('/dashboard_guardian')
def dashboard_guardian():
    return render_template('dashboards/dashboard_guardian.html')


@app.route('/dashboard_caretaker')
def dashboard_caretaker():
    try:
        # Fetch all bookings from the Booking table
        bookings = Booking.query.all()
        
        # Convert the bookings to a list of dictionaries
        bookings_list = []
        for booking in bookings:
            bookings_list.append({
                'id': booking.booking_id,
                'user_email': booking.user_email,
                'caretaker_email': booking.caretaker_email,
                'service': booking.service,
                'booking_date': booking.booking_date,
                'status': booking.status.name,
                'latitude': booking.latitude,
                'longitude': booking.longitude
            })
        
        return render_template('dashboards/dashboard_caretaker.html', bookings=bookings_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes and Views ----------------------------------
# -------------------------------------------------------------------------------------------------

@app.route('/about')
def about():
    return render_template('routes/about.html')

@app.route('/profile')
def profile():
    if "email" in session:
        email = session['email']
        user = User.query.filter_by(email=email).first_or_404()
        guardian_relation = GuardianElderly.query.filter_by(elderly_email=user.email).first()
        guardian_linked = False
        guardian = None
        if guardian_relation:
            guardian_email = guardian_relation.guardian_email
            guardian = User.query.filter_by(email=guardian_email).first()
            guardian_linked = True if guardian else False
        
        return render_template('routes/profile.html', user=user, guardian=guardian, guardian_linked=guardian_linked)
@app.route('/profile_caretaker')
def caretaker_profile():
    return render_template('routes/caretakerprofile.html')

@app.route('/emergency')
def emergency():
    return render_template('routes/emergency.html')

@app.route('/homecare')
def homecare():
    return render_template('routes/homecare.html')

@app.route('/medicalcare')
def medicalcare():
    return render_template('routes/medicalcare.html')

@app.route('/contact')
def contact():
    return render_template('routes/contact.html')

@app.route('/community')
def community():
    return render_template('routes/community.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'username' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        service = request.form['service']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Combine date and time into datetime objects
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

        # Create a new booking instance
        new_booking = Booking(
            users_email=user.email,
            service=service,
            status=BookingStatus.pending,
            latitude=latitude,
            longitude=longitude
        )

        db.session.add(new_booking)
        db.session.commit()

        flash('Service booked successfully!', 'success')
        return redirect(url_for('thanks'))

    return render_template('routes/booking.html')



@app.route('/fitness')
def fitness():
    return render_template('routes/fitness.html')

@app.route('/health')
def health():
    return render_template('routes/health.html')

@app.route('/services')
def services():
    return render_template('routes/services.html')

@app.route('/testimonials')
def testimonials():
    return render_template('routes/testimonials.html')

@app.route('/user')
def user():
    return render_template('routes/user.html')

@app.route('/reminder', methods=['GET', 'POST'])
def medicinereminder():
    if 'username' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

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
            user_email=user.email
        )

        db.session.add(new_medicine_reminder)
        db.session.commit()

        flash('Medicine reminder added successfully!', 'success')
        return redirect(url_for('medicinereminder'))

    # Fetch the medicine reminders for the current user
    medicine_reminders = MedicineReminder.query.filter_by(user_email=user.email).all()
    return render_template('routes/reminder.html', medicine_reminders=medicine_reminders)

@app.route('/appointreminder', methods=['GET', 'POST'])
def appointreminder():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        # Retrieve form data
        appointment_name = request.form['appointment_name']
        location = request.form['location']
        time = request.form['time']
        date = request.form['date']

        # Save the appointment reminder in the database
        new_appointment_reminder = AppointmentReminder(
            appointment_name=appointment_name,
            location=location,
            time=time,  # Store time as a string
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            user_email=user.email
        )

        db.session.add(new_appointment_reminder)
        db.session.commit()

        flash('Appointment reminder added successfully!', 'success')
        return redirect(url_for('appointreminder'))

    # Fetch the appointment reminders for the current user
    appointment_reminders = AppointmentReminder.query.filter_by(user_email=user.email).all()
    return render_template('routes/appointreminder.html', appointments=appointment_reminders)
@app.route('/newservice')
def newservice():
    return render_template('routes/newservice.html')

@app.route('/thanks')
def thanks():
    return render_template('routes/thanks.html')

@app.route('/caretakerprofile')
def caretakerprofile():
    return render_template('routes/caretakerprofile.html')

@app.route('/dashservices')
def dashservices():
    return render_template('routes/dashservices.html')

@app.route('/sos')
def sos():
    return render_template('routes/sos.html')

@app.route('/yourhealth')
def yourhealth():
    return render_template('routes/yourhealth.html')

# Route to create sample data
app.route('/create_sample_data')
def create_sample_data():
    print("Creating sample data...\n\n")

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
        guardian_email=guardian_user.email,
        elderly_email=elderly_user.email
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

    print("Sample data created successfully!")
    

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Running Python Script -----------------------------
# -------------------------------------------------------------------------------------------------


# To autodelete the instance and __pychache__ folders when closing flask app 
def prompt_and_delete_folders():
    folders_to_delete = ['instance', '__pycache__']
    print('\n')
    for folder in folders_to_delete:
        if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)
                print(f"Deleted folder: {folder}")


if __name__ == '__main__':
    with app.app_context():
        create_sample_user()
        # create_sample_booking()
        db.create_all()

    # #For disabling the flask logs
    # import logging
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)
    # atexit.register(prompt_and_delete_folders)
    app.run(debug=True)
#     app.run(host='192.168.29.235', port=5000,debug=True)
