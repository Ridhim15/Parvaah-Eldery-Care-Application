import email
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
<<<<<<< Updated upstream
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
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

        user = Elderly.query.filter_by(username=username).first()
        if user:
            return make_response('User already exists', 400)
=======
        print(f'full_name: {full_name}, password: {password}, email: {email}')
        # Check if the username already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return redirect(url_for('login'))
>>>>>>> Stashed changes
        else:
            session['username'] = full_name
            session['email'] = email
<<<<<<< Updated upstream
            new_user = Elderly(username=username, password=password, email=email)
=======
            # Create a new user and save it to the database
            hashed_password = generate_password_hash(password)
            new_user = User(full_name=full_name, password=hashed_password, email=email, role=UserRole.elderly)
>>>>>>> Stashed changes
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.full_name
            session['email'] = new_user.email
            session['profile_image'] = new_user.profile_image if new_user.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
<<<<<<< Updated upstream
            return redirect(url_for('dashboard'))
    return make_response('Invalid request method', 405)

=======
            
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
        create_user_health_table(username)

        # Redirect to the dashboard after form submission
        return redirect(url_for('dashboard'))

    user = User.query.filter_by(full_name=session['username']).first()
    return render_template('form.html', user=user)

def create_user_health_table(username):
    """Dynamically create a table for each user to store their health records."""
    table_name = f"health_{username}"
    query = text(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, date DATE, sugar INTEGER, bp_sys INTEGER, bp_dia INTEGER)")
    db.session.execute(query)
    db.session.commit()

>>>>>>> Stashed changes
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("LOGIN attempted")
    if request.method == 'POST':
        print('Huh, this is /login')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
<<<<<<< Updated upstream
        elderly = Elderly.query.filter_by(username=username, password=password).first()

        if elderly:
            session['username'] = elderly.username
            session['user_id'] = elderly.eid
            session['profile_image'] = elderly.profile_image if elderly.profile_image else url_for('static', filename='assets/images/profile_def_m.png')
=======
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
>>>>>>> Stashed changes
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    print(f'{session["username"]} logged out successfully')
    print(f'{session['email']}: session["email"]')
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

<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes and Views ----------------------------------
# -------------------------------------------------------------------------------------------------


@app.route('/about')
def about():
    return render_template('about.html')

<<<<<<< Updated upstream
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
 
=======
 



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

>>>>>>> Stashed changes
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(full_name=session['username']).first()
    health = db.session.execute(text(f"SELECT * FROM health_info")).fetchall()

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

<<<<<<< Updated upstream
@app.route('/booking')
def booking():
=======









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

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
@app.route('/reminder')
def reminder():
    return render_template('reminder.html')

@app.route('/appointreminder')
def appointreminder():
    return render_template('appointreminder.html')
=======
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

>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
=======
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


>>>>>>> Stashed changes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
