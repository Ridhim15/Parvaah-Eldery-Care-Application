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
