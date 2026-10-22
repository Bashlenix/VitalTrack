from models import Doctor
from tests.conftest import flashed_messages, login


def test_confirmed_doctor_can_log_in(client, make_doctor):
    doctor = make_doctor()
    response = login(client, "dr_a")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as session:
        assert session["doctor_id"] == doctor.id


def test_wrong_password_is_rejected(client, make_doctor):
    make_doctor()
    response = login(client, "dr_a", "Wrong0rd!")
    assert response.headers["Location"].endswith("/login")
    assert "Invalid username/email or password." in flashed_messages(client)


def test_unconfirmed_doctor_cannot_log_in(client, make_doctor):
    make_doctor(confirmed=False)
    login(client, "dr_a")
    assert any("confirm your email" in m for m in flashed_messages(client))
    with client.session_transaction() as session:
        assert "doctor_id" not in session


def test_registration_creates_unconfirmed_doctor(client):
    response = client.post(
        "/registration/register",
        data={
            "firstName": "New",
            "lastName": "Doctor",
            "username": "dr_new",
            "email": "new@example.com",
            "password": "Passw0rd!",
            "speciality": "Neurology",
        },
    )
    assert response.headers["Location"].endswith("/registration/register_success")
    doctor = Doctor.query.filter_by(username="dr_new").one()
    assert doctor.email_confirmed is False


def test_logout_clears_session(client, make_doctor):
    make_doctor()
    login(client, "dr_a")
    client.get("/logout")
    with client.session_transaction() as session:
        assert "doctor_id" not in session
