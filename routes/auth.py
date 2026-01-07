"""
Authentication and user management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Doctor, Specialty
from utils.token_holper import load_token
from utils.validators import validate_password, validate_email
from services.email_service import EmailService
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Display login page or handle login submission."""
    if request.method == "GET":
        return render_template("login/login.html")
    return login_user()


def login_user():
    """
    Handle doctor login.
    """
    try:
        username_or_email = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username_or_email or not password:
            flash("Username/email and password are required.", "error")
            return redirect(url_for("auth.login"))

        doctor = Doctor.query.filter(
            (Doctor.username == username_or_email) | (Doctor.email == username_or_email)
        ).first()

        if not doctor or not check_password_hash(doctor.password, password):
            flash("Invalid username/email or password.", "error")
            return redirect(url_for("auth.login"))

        if not doctor.email_confirmed:
            flash(
                "Please confirm your email address before logging in. "
                "Check your email for the confirmation link.",
                "warning",
            )
            return redirect(url_for("auth.login"))

        # Set session variables
        session["doctor_id"] = doctor.id
        session["doctor_name"] = f"Dr. {doctor.last_name}"
        session["logged_in"] = True
        session["doctor_specialty"] = (
            doctor.specialties[0].name if doctor.specialties else "General"
        )

        flash(f"Welcome back, Dr. {doctor.last_name}!", "success")
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        flash(f"An error occurred during login: {str(e)}", "error")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Handle forgot password requests."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("auth.forgot_password"))
        doctor = Doctor.query.filter_by(email=email).first()
        if not doctor:
            flash("No account found with that email address.", "error")
            return redirect(url_for("auth.forgot_password"))
        if EmailService.send_password_reset_email(doctor):
            flash("Password reset email sent. Please check your inbox.", "info")
        else:
            flash("Failed to send password reset email. Please try again.", "error")
        return redirect(url_for("auth.forgot_password"))
    return render_template("password/forgot_password_form.html")


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset using the provided token."""
    try:
        doctor_id = load_token(
            token,
            current_app.config["MAX_AGE_SECONDS"],
            expected_purpose="reset_password",
        )
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            flash("Invalid or expired reset link.", "error")
            return redirect(url_for("auth.login"))
        if request.method == "POST":
            new_password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            if not new_password or not confirm_password:
                flash("Both password fields are required.", "error")
                return render_template("password/reset_password_form.html")
            if new_password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("password/reset_password_form.html")
            is_valid, msg = validate_password(new_password)
            if not is_valid:
                flash(msg, "error")
                return render_template("password/reset_password_form.html")
            doctor.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password reset successfully! You can now log in.", "success")
            return redirect(url_for("auth.login"))
        return render_template("password/reset_password_form.html")
    except Exception:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.login"))


@auth_bp.route("/registration/register.html")
def register():
    """Display registration page."""
    return render_template("registration/register.html")


@auth_bp.route("/registration/register_success")
def register_success():
    """Display registration success page."""
    return render_template("registration/register_success.html")


@auth_bp.route("/registration/register", methods=["POST"])
def register_doctor():
    """Handle doctor registration."""
    try:
        # Get form data
        first_name = request.form.get("firstName", "").strip()
        last_name = request.form.get("lastName", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        phone_number = request.form.get("phone", "").strip()
        specialty_name = request.form.get("speciality", "").strip()

        errors = []

        if not last_name:
            errors.append("Last name is required")
        if not username:
            errors.append("Username is required")
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")

        # Email format validation
        if email and not validate_email(email):
            errors.append("Invalid email format")

        # Password strength validation
        if password:
            is_valid, msg = validate_password(password)
            if not is_valid:
                errors.append(msg)

        # Username validation
        if username and (len(username) < 3 or len(username) > 20):
            errors.append("Username must be between 3 and 20 characters")

        # Check for existing username or email
        if username or email:
            existing_doctor = Doctor.query.filter(
                (Doctor.username == username) | (Doctor.email == email)
            ).first()

            if existing_doctor:
                if existing_doctor.username == username:
                    errors.append("Username already exists")
                if existing_doctor.email == email:
                    errors.append("Email already exists")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("auth.register"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new doctor
        new_doctor = Doctor(
            first_name=first_name if first_name else None,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_password,
            phone_number=phone_number if phone_number else None,
            email_confirmed=False,  # Email not confirmed yet
        )

        # Handle specialty if provided
        if specialty_name:
            specialty = Specialty.query.filter_by(name=specialty_name).first()
            if not specialty:
                specialty = Specialty(name=specialty_name)
                db.session.add(specialty)

            new_doctor.specialties.append(specialty)

        # Add to database
        db.session.add(new_doctor)
        db.session.commit()

        # Send confirmation email
        email_sent = EmailService.send_confirmation_email(new_doctor)

        if email_sent:
            flash(
                f"Registration successful! A confirmation email has been sent "
                f"to {email}. Please check your email to activate your account.",
                "success",
            )
        else:
            flash(
                "Registration successful! However, we couldn't "
                "send the confirmation email. Please contact support.",
                "warning",
            )

        return redirect(url_for("auth.register_success"))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during registration: {str(e)}", "error")
        return redirect(url_for("auth.register"))


@auth_bp.route("/confirm/<token>")
def confirm_email(token):
    """Handle email confirmation."""
    try:
        # Token expires in 24 hours (86400 seconds)
        doctor_id = load_token(
            token, current_app.config["MAX_AGE_SECONDS"], expected_purpose="confirm"
        )

        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            flash("Invalid confirmation link.", "error")
            return redirect(url_for("auth.login"))

        if doctor.email_confirmed:
            flash("Email already confirmed. Please log in.", "info")
            return redirect(url_for("auth.login"))

        # Confirm the email
        doctor.email_confirmed = True
        doctor.email_confirmed_at = datetime.utcnow()
        db.session.commit()

        flash("Email confirmed successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    except Exception:
        flash("Invalid or expired confirmation link.", "error")
        return redirect(url_for("auth.login"))
