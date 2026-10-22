"""
Deployment safety: patient uploads must never end up inside the image, and
the app must refuse to start with settings that break sessions.
"""

import pathlib

import pytest

from app import create_app

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_dockerignore_excludes_old_static_upload_folder():
    # Older installs kept patient images in static/uploads; copying them into
    # the image would serve them from /static without login
    lines = (ROOT / ".dockerignore").read_text().splitlines()
    assert "static/uploads/" in lines


def test_dockerfile_refuses_to_build_with_static_uploads():
    assert "RUN test ! -e static/uploads" in (ROOT / "Dockerfile").read_text()


def test_missing_secret_key_fails_fast():
    # Each gunicorn worker would otherwise invent its own key and reject
    # cookies and CSRF tokens signed by the other workers
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SECRET_KEY": None, "TESTING": False})


def test_testing_without_secret_key_still_starts():
    assert create_app({"SECRET_KEY": None, "TESTING": True}).config["SECRET_KEY"]
