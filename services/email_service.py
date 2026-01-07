"""
Email service for handling email operations in the EHR system.
"""

from flask import render_template, url_for
from utils.mail_helper import send_email
from utils.token_holper import generate_token


class EmailService:
    """Service class for email-related operations."""

    @staticmethod
    def send_confirmation_email(doctor) -> bool:
        """Send email confirmation to new doctor."""
        try:
            token = generate_token(doctor.id, "confirm")
            confirm_url = url_for("auth.confirm_email", token=token, _external=True)

            html = render_template(
                "email/email_confirmation.html",
                last_name=doctor.last_name,
                confirm_url=confirm_url,
            )

            send_email(
                subject="Confirm your VitalTrack EHR System account",
                recipients=[doctor.email],
                html=html,
            )
            return True

        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
            return False

    @staticmethod
    def send_password_reset_email(doctor) -> bool:
        """Send password reset email to doctor."""
        try:
            token = generate_token(doctor.id, "reset_password")
            reset_url = url_for("auth.reset_password", token=token, _external=True)

            html = render_template(
                "email/password_reset_template.html", doctor=doctor, reset_url=reset_url
            )

            send_email(
                subject="Reset your VitalTrack EHR System password",
                recipients=[doctor.email],
                html=html,
            )
            return True

        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
