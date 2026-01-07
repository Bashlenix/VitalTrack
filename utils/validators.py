"""
Validation utilities for the EHR system.
"""

import re
from typing import Tuple
from werkzeug.security import generate_password_hash


def validate_email(email: str) -> bool:
    """Validate email format. Return True if valid, False otherwise."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength.
    Return Tuple of (bool, str) where bool is True if valid,
    False otherwise and str is the error message."""

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"


def hash_password(password: str) -> str:
    """Hash a password using werkzeug's password hashing."""
    return generate_password_hash(password)
