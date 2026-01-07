#!/usr/bin/env python3
"""
Create a test doctor account for the EHR system
"""
from app import create_app
from models import db, Doctor
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        # Check if test doctor already exists
        existing_doctor = Doctor.query.filter(
            (Doctor.username == "testdoctor") | (Doctor.email == "doctor@test.com")
        ).first()

        if existing_doctor:
            print("✅ Test doctor already exists:")
            print(f"   Username: {existing_doctor.username}")
            print(f"   Email: {existing_doctor.email}")
            print(f"   Email confirmed: {existing_doctor.email_confirmed}")

            # Confirm email if not confirmed
            if not existing_doctor.email_confirmed:
                existing_doctor.email_confirmed = True
                db.session.commit()
                print("✅ Email confirmed for existing test doctor")

        else:
            # Create test doctor
            test_doctor = Doctor(
                first_name="Test",
                last_name="Doctor",
                username="testdoctor",
                email="doctor@test.com",
                password=generate_password_hash("password123"),
                phone_number="123-456-7890",
                email_confirmed=True,  # Skip email confirmation for test
            )

            db.session.add(test_doctor)
            db.session.commit()

            print("✅ Test doctor created successfully!")
            print("   Username: testdoctor")
            print("   Email: doctor@test.com")
            print("   Password: password123")
            print("   Email confirmed: True")

        print("\n🔐 You can now login with:")
        print("   Username/Email: testdoctor OR doctor@test.com")
        print("   Password: password123")

    except Exception as e:
        print(f"❌ Error creating test doctor: {e}")
        db.session.rollback()
