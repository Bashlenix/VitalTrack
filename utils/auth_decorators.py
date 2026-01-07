"""
Authentication utilities for the EHR system.
"""

from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    """Decorator to ensure user is logged in before accessing protected routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
