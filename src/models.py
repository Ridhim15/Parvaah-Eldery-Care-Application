from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    guardian = "guardian"
    elderly = "elderly"

class User(db.Model):
    __tablename__ = 'users'  # Corrected table name definition

    user_id = db.Column(db.Integer, primary_key=True)  # Primary Key
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    profile_image = db.Column(db.String(200), default='/static/assets/images/profile_def_m.png')
    role = db.Column(db.Enum(UserRole), nullable=False)  # Elderly or Guardian

    # Additional Fields for Elderly
    gender = db.Column(db.String(100))
    dob = db.Column(db.Date)
    phone_no = db.Column(db.String(15), unique=True)
    address = db.Column(db.String(500))
    disease = db.Column(db.String(200))
    blood_type = db.Column(db.String(5))
    additional_health_details = db.Column(db.String(500))
    
    # Guardian-Elderly Relationship (One Guardian per Elderly)
    guardian = db.relationship('GuardianElderly', backref='elderly_user', uselist=False, primaryjoin="User.email == GuardianElderly.elderly_email", lazy=True)
    elderly_user = db.relationship('GuardianElderly', backref='guardian_user', uselist=False, primaryjoin="User.email == GuardianElderly.guardian_email", lazy=True)

    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>"
class GuardianElderly(db.Model):
    __tablename__ = 'guardian_elderly'  # Corrected table name definition

    id = db.Column(db.Integer, primary_key=True)
    guardian_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False, unique=True)  # Link to guardian email
    elderly_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False, unique=True)   # Link to elderly email

    def __repr__(self):
        return f"<GuardianElderly (Guardian: {self.guardian_email}, Elderly: {self.elderly_email})>"

class BookingStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Who made the booking
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretakers.caretaker_id'), nullable=True)  # Assigned caretaker
    service = db.Column(db.String(100), nullable=False)  # Service booked
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Booking date
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.pending)  # Booking status

    def _repr_(self):
        return f"<Booking {self.booking_id} (Status: {self.status})>"

class MedicineReminder(db.Model):
    __tablename__ = 'medicine_reminders'

    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.Integer, nullable=False)  # Number of times to take the medicine
    times = db.Column(db.String(500), nullable=False)  # Store multiple times as a comma-separated string
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def _repr_(self):
        return f"<MedicineReminder {self.medicine_name} for User {self.user_id}>"

class Caretaker(db.Model):
    __tablename__ = 'caretakers'

    caretaker_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    phone_no = db.Column(db.String(15), unique=True)
    available = db.Column(db.Boolean, default=True)  # Availability status

    # Relationship with Bookings
    bookings = db.relationship('Booking', backref='caretaker', lazy=True)

    def _repr_(self):
        return f"<Caretaker {self.full_name}>"

class AppointmentReminder(db.Model):
    __tablename__ = 'appointment_reminders'
    id = db.Column(db.Integer, primary_key=True)
    appointment_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def _repr_(self):
        return f"<AppointmentReminder {self.appointment_name} for User {self.user_id}>"
