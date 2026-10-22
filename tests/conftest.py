"""
Shared pytest fixtures for the EHR system.
"""

import os

# config.py reads the environment at import time and load_dotenv() would
# otherwise pick up a developer's .env, so set test values before importing app
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SECURITY_PASSWORD_SALT"] = "test-salt"
os.environ.pop("DB_HOST", None)

from datetime import date  # noqa: E402

import pytest  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

from app import create_app  # noqa: E402
from models import db, Doctor, Patient, GenderEnum  # noqa: E402


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret-key",
            "SECURITY_PASSWORD_SALT": "test-salt",
            "WTF_CSRF_ENABLED": False,
            "MAIL_SUPPRESS_SEND": True,
            "MAIL_DEFAULT_SENDER": "test@example.com",
            "UPLOAD_FOLDER": str(tmp_path),
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_doctor(app):
    def _make_doctor(
        username="dr_a", email="a@example.com", password="Passw0rd!", confirmed=True
    ):
        doctor = Doctor(
            first_name="Ada",
            last_name=username.capitalize(),
            username=username,
            email=email,
            password=generate_password_hash(password),
            email_confirmed=confirmed,
        )
        db.session.add(doctor)
        db.session.commit()
        return doctor

    return _make_doctor


@pytest.fixture
def make_patient(app):
    def _make_patient(doctor, first_name="Jane"):
        patient = Patient(
            first_name=first_name,
            last_name="Doe",
            gender=GenderEnum.FEMALE,
            date_of_birth=date(1990, 1, 1),
            doctor_id=doctor.id,
        )
        db.session.add(patient)
        db.session.commit()
        return patient

    return _make_patient


def login(client, username, password="Passw0rd!"):
    return client.post("/login", data={"username": username, "password": password})


def flashed_messages(client):
    with client.session_transaction() as session:
        return [message for _category, message in session.get("_flashes", [])]
