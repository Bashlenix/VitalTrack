import pathlib
import re

import pytest

from tests.conftest import flashed_messages

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "templates"


@pytest.fixture
def csrf_client(app):
    app.config["WTF_CSRF_ENABLED"] = True
    return app.test_client()


def test_login_post_without_csrf_token_is_rejected(csrf_client):
    response = csrf_client.post("/login", data={"username": "a", "password": "b"})
    assert response.status_code == 400


def test_rejected_post_explains_and_is_logged(csrf_client, caplog):
    response = csrf_client.post("/login", data={"username": "a", "password": "b"})
    assert "Your session expired or the form was invalid" in response.get_data(as_text=True)
    assert any("CSRF check failed" in record.getMessage() for record in caplog.records)


def test_login_post_with_csrf_token_is_accepted(csrf_client, make_doctor):
    make_doctor()
    page = csrf_client.get("/login").get_data(as_text=True)
    token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)
    response = csrf_client.post(
        "/login", data={"username": "dr_a", "password": "Passw0rd!", "csrf_token": token}
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert flashed_messages(csrf_client)


def post_forms():
    for template in sorted(TEMPLATES.rglob("*.html")):
        html = template.read_text()
        forms = re.findall(r"<form\b.*?</form>", html, flags=re.S | re.I)
        for number, form in enumerate(forms, start=1):
            if re.search(r'method\s*=\s*["\']post["\']', form, flags=re.I):
                yield pytest.param(
                    template.relative_to(TEMPLATES), form, id=f"{template.relative_to(TEMPLATES)}#{number}"
                )


@pytest.mark.parametrize("template, form", list(post_forms()))
def test_every_post_form_has_csrf_token(template, form):
    assert "csrf_token()" in form, f"{template} has a POST form without csrf_token"


def test_base_template_exposes_csrf_token_for_scripts():
    assert re.search(
        r'<meta name="csrf-token" content="{{ csrf_token\(\) }}">',
        (TEMPLATES / "main" / "base.html").read_text(),
    )


def script_built_post_forms():
    for template in sorted(TEMPLATES.rglob("*.html")):
        scripts = re.findall(r"createElement\('form'\).*?\.submit\(\)", template.read_text(), flags=re.S)
        for number, script in enumerate(scripts, start=1):
            yield pytest.param(script, id=f"{template.relative_to(TEMPLATES)}#{number}")


@pytest.mark.parametrize("script", list(script_built_post_forms()))
def test_every_script_built_form_sends_csrf_token(script):
    assert "meta[name=csrf-token]" in script and "csrf_token" in script
    assert "if (csrfToken)" not in script, "token must always be sent, not only when present"
