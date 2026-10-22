"""
Internal error details (database messages, hostnames) must be logged for
the team, never shown to the user.
"""

import pytest
from sqlalchemy.exc import IntegrityError

import routes.auth
import routes.patients
from models import db, Doctor
from tests.conftest import flashed_messages, login

SECRET = "SECRET-DB-DETAIL mysql-host:3306"


def boom(*args, **kwargs):
    raise RuntimeError(SECRET)


def assert_logged(caplog):
    assert any(SECRET in (record.exc_text or "") for record in caplog.records)


def test_login_error_is_logged_not_shown(client, make_doctor, monkeypatch, caplog):
    make_doctor()
    monkeypatch.setattr(routes.auth, "check_password_hash", boom)
    login(client, "dr_a")
    messages = flashed_messages(client)
    assert messages and all(SECRET not in m for m in messages)
    assert_logged(caplog)


def test_patient_save_error_is_logged_not_shown(client, make_doctor, monkeypatch, caplog):
    make_doctor()
    login(client, "dr_a")
    monkeypatch.setattr(db.session, "commit", boom)
    response = client.post(
        "/add_patient",
        data={"first_name": "Jane", "last_name": "Roe", "gender": "female", "date_of_birth": "1990-01-01"},
    )
    body = response.get_data(as_text=True)
    assert "Could not save the patient" in body
    assert SECRET not in body
    assert_logged(caplog)


class BrokenDate:
    @staticmethod
    def today():
        boom()


def test_patient_list_error_is_logged_not_shown(client, make_doctor, monkeypatch, caplog):
    make_doctor()
    login(client, "dr_a")
    monkeypatch.setattr(routes.patients, "date", BrokenDate)
    client.get("/patients")
    messages = flashed_messages(client)
    assert messages and all(SECRET not in m for m in messages)
    assert_logged(caplog)


def test_database_errors_do_not_carry_patient_data(app, make_doctor):
    # Logged exceptions must not include SQL parameter values (names, emails)
    make_doctor(email="phi.patient@example.com")
    db.session.add(Doctor(last_name="X", username="other", email="phi.patient@example.com", password="x"))
    with pytest.raises(IntegrityError) as error:
        db.session.commit()
    db.session.rollback()
    assert "phi.patient@example.com" not in str(error.value)
