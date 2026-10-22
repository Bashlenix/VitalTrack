"""
Integration tests against the running Docker Compose stack (app + MySQL).
Skipped unless VITALTRACK_BASE_URL is set, e.g. http://localhost:5001.
Uses only the standard library so the CI runner needs no extra packages.
"""

import http.cookiejar
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid

import pytest

pytestmark = pytest.mark.integration

BASE_URL = os.getenv("VITALTRACK_BASE_URL")
if not BASE_URL:
    pytest.skip("VITALTRACK_BASE_URL not set", allow_module_level=True)

# Seeded by db/init.sql; patient 1 (Talerson) and this image belong to doctor 1,
# not to the CI doctor
SEED_PATIENT_ID = 1
SEED_PATIENT_LAST_NAME = "Talerson"
SEED_IMAGE = "patient_1/d5ed01cd-c8c2-446b-8ab1-d29d9a43b225.png"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get_status(path, follow_redirects=False, opener=None):
    if opener is None:
        handlers = [] if follow_redirects else [NoRedirect()]
        opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(BASE_URL + path, timeout=10) as response:
            return response.status, response.headers, response.read().decode(errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.headers, ""


def csrf_token_from(html):
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None


def post_multipart(opener, path, fields, file_field, filename, content):
    _, _, page = get_status(path, opener=opener)
    token = csrf_token_from(page)
    if token:
        fields = {**fields, "csrf_token": token}
    boundary = uuid.uuid4().hex
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
        for name, value in fields.items()
    ]
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
        f'filename="{filename}"\r\nContent-Type: image/png\r\n\r\n'.encode()
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )
    request = urllib.request.Request(
        BASE_URL + path,
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with opener.open(request, timeout=10) as response:
        return response.geturl(), response.read().decode(errors="replace")


def post_form(opener, path, fields):
    _, _, page = get_status(path, opener=opener)
    token = csrf_token_from(page)
    if token:
        fields = {**fields, "csrf_token": token}
    data = urllib.parse.urlencode(fields).encode()
    with opener.open(BASE_URL + path, data=data, timeout=10) as response:
        return response.geturl(), response.read().decode()


@pytest.fixture(scope="module")
def cookies():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    final_url, _ = post_form(
        opener,
        "/login",
        {
            "username": os.environ["CI_DOCTOR_USERNAME"],
            "password": os.environ["CI_DOCTOR_PASSWORD"],
        },
    )
    assert final_url.endswith("/dashboard"), "CI doctor login failed"
    return jar


@pytest.fixture
def doctor_session(cookies):
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))


@pytest.fixture
def doctor_session_no_redirect(cookies):
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies), NoRedirect()
    )


def test_health_reports_database_ok():
    status, _, body = get_status("/health")
    assert status == 200
    assert '"database":"ok"' in body.replace(" ", "")


def test_login_page_renders():
    status, _, _ = get_status("/login")
    assert status == 200


def test_dashboard_redirects_anonymous_user_to_login():
    status, headers, _ = get_status("/dashboard")
    assert status == 302
    assert headers["Location"].endswith("/login")


def test_seed_radiology_image_not_served_statically():
    status, _, _ = get_status(f"/static/uploads/radiology/{SEED_IMAGE}")
    assert status == 404


def test_logged_in_doctor_sees_own_patient(doctor_session):
    status, _, body = get_status("/patients", opener=doctor_session)
    assert status == 200
    assert "Cipatient" in body


def test_logged_in_doctor_can_add_patient(doctor_session):
    last_name = "Itest" + uuid.uuid4().hex[:8]
    post_form(
        doctor_session,
        "/add_patient",
        {
            "first_name": "Live",
            "last_name": last_name,
            "gender": "female",
            "date_of_birth": "1975-03-02",
        },
    )
    _, _, body = get_status("/patients", opener=doctor_session)
    assert last_name.capitalize() in body


def test_doctor_cannot_open_other_doctors_patient(doctor_session):
    _, _, body = get_status(f"/patient/{SEED_PATIENT_ID}", opener=doctor_session)
    assert SEED_PATIENT_LAST_NAME not in body


def test_doctor_cannot_open_other_doctors_image(doctor_session_no_redirect):
    status, _, _ = get_status(
        f"/radiology_image/{SEED_IMAGE}", opener=doctor_session_no_redirect
    )
    assert status == 302


def test_uploaded_image_only_reachable_by_owning_doctor(
    doctor_session, doctor_session_no_redirect
):
    image = b"\x89PNG\r\n\x1a\n" + uuid.uuid4().bytes
    _, _, before = get_status("/view_radiology_imaging", opener=doctor_session)
    _, page = post_multipart(
        doctor_session,
        "/add_radiology_imaging",
        {
            "patient_id": os.environ["CI_PATIENT_ID"],
            "imaging_name": "Integration X-ray",
            "imaging_date": "2026-01-02T10:30",
        },
        "image_file",
        "xray.png",
        image,
    )
    image_path = r"/radiology_image/(patient_\d+/[0-9a-f-]+\.png)"
    new_paths = set(re.findall(image_path, page)) - set(re.findall(image_path, before))
    assert len(new_paths) == 1, "uploaded image not listed"
    path = new_paths.pop()

    status, _, _ = get_status(f"/radiology_image/{path}", opener=doctor_session_no_redirect)
    assert status == 200
    assert get_status(f"/radiology_image/{path}")[0] == 302
    assert get_status(f"/static/uploads/radiology/{path}")[0] == 404
