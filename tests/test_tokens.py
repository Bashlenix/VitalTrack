import pytest
from itsdangerous import SignatureExpired

from utils.token_holper import generate_token, load_token


def test_token_round_trip_returns_doctor_id(app):
    token = generate_token(5, "confirm")
    assert load_token(token, 60, "confirm") == 5


def test_token_with_wrong_purpose_is_rejected(app):
    token = generate_token(5, "confirm")
    with pytest.raises(ValueError):
        load_token(token, 60, "reset_password")


def test_expired_token_is_rejected(app):
    token = generate_token(5, "confirm")
    with pytest.raises(SignatureExpired):
        load_token(token, -1, "confirm")
