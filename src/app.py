from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text for raw SQL queries
import mysql.connector

app = Flask(__name__)

# Configure the app for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admin@localhost/parvaah'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a simple model for Elderly
class Elderly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)  # Ensure this is not NULL
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Elderly {self.username}>'

# Route to test the database connection
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
            age=70,
            image_url='https://example.com/testuser.jpg'  # Add a sample image URL
        )
        db.session.add(new_elderly)
        db.session.commit()
        return "Test data added successfully!"
    except Exception as e:
        return f"Error adding test data: {str(e)}"

# Initialize the database and create tables if they don't exist
with app.app_context():
    db.create_all()

# Routes for other pages
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
    app.run(debug=True)
