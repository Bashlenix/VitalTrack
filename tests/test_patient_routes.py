from datetime import datetime

from models import db, Appointment, Patient
from tests.conftest import login

NEW_PATIENT = {
    "first_name": "Jane",
    "last_name": "Roe",
    "gender": "female",
    "date_of_birth": "1990-01-01",
}


def test_add_patient_belongs_to_logged_in_doctor(client, make_doctor):
    doctor = make_doctor()
    login(client, "dr_a")
    response = client.post("/add_patient", data=NEW_PATIENT)
    assert response.status_code == 302
    patient = Patient.query.filter_by(last_name="Roe").one()
    assert patient.doctor_id == doctor.id


def test_edit_patient_changes_last_name(client, make_doctor, make_patient):
    patient = make_patient(make_doctor())
    login(client, "dr_a")
    client.post(f"/edit_patient/{patient.id}", data={**NEW_PATIENT, "last_name": "Smith"})
    assert db.session.get(Patient, patient.id).last_name == "Smith"


def test_delete_patient_removes_patient_and_appointments(client, make_doctor, make_patient):
    doctor = make_doctor()
    patient = make_patient(doctor)
    db.session.add(
        Appointment(patient_id=patient.id, doctor_id=doctor.id, date=datetime(2030, 1, 1, 9))
    )
    db.session.commit()
    login(client, "dr_a")
    client.post(f"/delete_patient/{patient.id}")
    assert db.session.get(Patient, patient.id) is None
    assert Appointment.query.count() == 0
