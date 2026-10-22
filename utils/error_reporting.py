"""
Error reporting for the EHR system: full details go to the server log,
users only see a generic message (no database or host internals).
"""

from flask import current_app, flash


def report_error(message: str) -> None:
    """Log the exception being handled and flash a generic message.
    Call from inside an `except` block."""
    current_app.logger.exception(message)
    flash(f"{message}. Please try again or contact support.", "error")
