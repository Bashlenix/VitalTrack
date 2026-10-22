"""
Create a confirmed doctor with one patient for integration tests.
Registration needs email confirmation and CI has no mail server, so the
pipeline creates the account directly. Safe to run more than once.

Usage (inside the web container):
    CI_DOCTOR_USERNAME=... CI_DOCTOR_EMAIL=... CI_DOCTOR_PASSWORD=... \
        python scripts/create_ci_doctor.py
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash  # noqa: E402

from app import app  # noqa: E402
from models import db, Doctor, Patient, GenderEnum  # noqa: E402

with app.app_context():
    username = os.environ["CI_DOCTOR_USERNAME"]
    doctor = Doctor.query.filter_by(username=username).first()
    if not doctor:
        doctor = Doctor(
            first_name="Continuous",
            last_name="Integration",
            username=username,
            email=os.environ["CI_DOCTOR_EMAIL"],
            password=generate_password_hash(os.environ["CI_DOCTOR_PASSWORD"]),
            email_confirmed=True,
        )
        db.session.add(doctor)
        db.session.commit()

    patient = Patient.query.filter_by(doctor_id=doctor.id, last_name="Cipatient").first()
    if not patient:
        patient = Patient(
            first_name="Integration",
            last_name="Cipatient",
            gender=GenderEnum.OTHER,
            date_of_birth=date(1980, 5, 17),
            doctor_id=doctor.id,
        )
        db.session.add(patient)
        db.session.commit()

    print(patient.id)
