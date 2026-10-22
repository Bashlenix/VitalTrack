import pytest

from utils.validators import validate_email, validate_password


def test_validate_email_accepts_valid_address():
    assert validate_email("a@b.co")


def test_validate_email_rejects_missing_at_sign():
    assert not validate_email("bad")


@pytest.mark.parametrize(
    "password, expected_message",
    [
        ("Pa0!", "Password must be at least 8 characters long"),
        ("passw0rd!", "Password must contain at least one uppercase letter"),
        ("PASSW0RD!", "Password must contain at least one lowercase letter"),
        ("Password!", "Password must contain at least one digit"),
        ("Passw0rdx", "Password must contain at least one special character"),
    ],
)
def test_validate_password_rejects_weak_passwords(password, expected_message):
    assert validate_password(password) == (False, expected_message)


def test_validate_password_accepts_strong_password():
    assert validate_password("Passw0rd!") == (True, "Password is valid")
