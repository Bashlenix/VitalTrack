"""
Patient-data protection checks: clinical data must never be reachable
without login, and a doctor must only reach their own patients.
"""

import os

import pytest

from app import create_app
from tests.conftest import login

PROTECTED_PAGES = [
    "/dashboard",
    "/patients",
    "/patient/1",
    "/view_appointments",
    "/view_lab_results",
    "/view_radiology_imaging",
    "/add_patient",
    "/doctor_profile",
    "/radiology_image/patient_1/x.png",
]


def test_upload_folder_outside_static():
    # Uses the real default config: anything under static/ is served without login
    app = create_app()
    upload = os.path.abspath(app.config["UPLOAD_FOLDER"])
    static = os.path.abspath(app.static_folder)
    assert os.path.commonpath([upload, static]) != static


@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_pages_require_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_doctor_cannot_view_other_doctors_patient(client, make_doctor, make_patient):
    make_doctor("dr_a", "a@example.com")
    doctor_b = make_doctor("dr_b", "b@example.com")
    patient = make_patient(doctor_b, first_name="Secretname")
    login(client, "dr_a")
    response = client.get(f"/patient/{patient.id}")
    assert response.status_code == 302
    followed = client.get(response.headers["Location"])
    assert b"Secretname" not in followed.data


def test_doctor_cannot_view_other_doctors_image(app, make_doctor, make_patient):
    make_doctor("dr_a", "a@example.com")
    doctor_b = make_doctor("dr_b", "b@example.com")
    patient = make_patient(doctor_b)
    folder = os.path.join(app.config["UPLOAD_FOLDER"], f"patient_{patient.id}")
    os.makedirs(folder)
    with open(os.path.join(folder, "x.png"), "wb") as f:
        f.write(b"\x89PNG fake image")
    image_url = f"/radiology_image/patient_{patient.id}/x.png"

    client_a = app.test_client()
    login(client_a, "dr_a")
    assert client_a.get(image_url).status_code == 302

    client_b = app.test_client()
    login(client_b, "dr_b")
    response = client_b.get(image_url)
    assert response.status_code == 200
    assert response.data == b"\x89PNG fake image"
