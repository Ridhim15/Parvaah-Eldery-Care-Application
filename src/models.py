from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    guardian = "guardian"
    elderly = "elderly"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(200), default='/static/assets/images/profile_def_m.png')
    gender = db.Column(db.String(10))
    address = db.Column(db.String(200))
    dob = db.Column(db.Date)
    phone_no = db.Column(db.String(15))
    blood_type = db.Column(db.String(5))
    diseases = db.Column(db.String(200))
    additional_health_details = db.Column(db.String(500))

    guardian_email = db.Column(db.String(100))
    guardian_name = db.Column(db.String(100))
    guardian_address = db.Column(db.String(200))
    guardian_contact = db.Column(db.String(15))
    
    role = db.Column(db.Enum(UserRole), nullable=False)
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def __repr__(self):
        return f"<User {self.full_name} \nEmail {self.email} \nRole: ({self.role})>"

class GuardianElderly(db.Model):
    __tablename__ = 'guardian_elderly'
    id = db.Column(db.Integer, primary_key=True)
    guardian_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False, unique=True)  # Link to guardian email
    elderly_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False, unique=True)   # Link to elderly email

    def __repr__(self):
        return f"<GuardianElderly guardian_email={self.guardian_email} elderly_email={self.elderly_email}>"

class BookingStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False) 
    caretaker_email = db.Column(db.String(50), db.ForeignKey('caretakers.email'), nullable=True)
    service = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.pending, nullable=False)

    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    caretaker = db.relationship('Caretaker', backref=db.backref('accepted_bookings', lazy=True))

    def __repr__(self):
        return f"<Booking booking_id={self.booking_id} user_email={self.user_email} caretaker_email={self.caretaker_email} service={self.service} status={self.status}>"

class MedicineReminder(db.Model):
    __tablename__ = 'medicine_reminders'
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.Integer, nullable=False)
    times = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False)

    user = db.relationship('User', backref=db.backref('medicine_reminders', lazy=True))

    def __repr__(self):
        return f"<MedicineReminder id={self.id} medicine_name={self.medicine_name} dosage={self.dosage} times={self.times} start_date={self.start_date} end_date={self.end_date} user_id={self.user_id}>"

class Caretaker(db.Model):
    __tablename__ = 'caretakers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(15))
    address = db.Column(db.String(200))

    def __repr__(self):
        return f"<Caretaker id={self.id} full_name={self.full_name} email={self.email}>"

class AppointmentReminder(db.Model):
    __tablename__ = 'appointment_reminders'
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(50), db.ForeignKey('users.email'), nullable=False)

    user = db.relationship('User', backref=db.backref('appointment_reminders', lazy=True))

    def __repr__(self):
        return f"<AppointmentReminder id={self.id} appointment_date={self.appointment_date} description={self.description} user_email={self.user_email}>"

class HealthInfo(db.Model):
    __tablename__ = 'health_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.String(50))
    heart_rate = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('health_info', lazy=True))

    def __repr__(self):
        return f"<HealthInfo id={self.id} user_id={self.user_id} height={self.height} weight={self.weight} blood_pressure={self.blood_pressure} heart_rate={self.heart_rate}>"

print("\nTHIS IS MODELS.py and it ran successfully \n")
