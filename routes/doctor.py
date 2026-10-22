"""
Doctor profile management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from models import db, Doctor
from utils.auth_decorators import login_required
from utils.error_reporting import report_error

doctor_bp = Blueprint("doctor", __name__)


@doctor_bp.route("/doctor_profile")
@login_required
def doctor_profile():
    """Display doctor profile page."""
    doctor = Doctor.query.get(session["doctor_id"])
    if not doctor:
        flash("Doctor profile not found.", "error")
        return redirect(url_for("main.dashboard"))

    return render_template("doctor/doctor_profile.html", doctor=doctor)


@doctor_bp.route("/edit_doctor_profile", methods=["GET", "POST"])
@login_required
def edit_doctor_profile():
    """Edit doctor profile."""
    doctor = Doctor.query.get(session["doctor_id"])
    if not doctor:
        flash("Doctor profile not found.", "error")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        try:
            # Update doctor information
            doctor.first_name = request.form["first_name"]
            doctor.last_name = request.form["last_name"]
            doctor.phone_number = request.form["phone_number"]
            doctor.email = request.form["email"]

            # Update session doctor name if last name changed
            session["doctor_name"] = f"Dr. {doctor.last_name}"

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("doctor.doctor_profile"))

        except Exception:
            db.session.rollback()
            report_error("Error updating profile")
            return render_template("doctor/edit_doctor_profile.html", doctor=doctor)

    return render_template("doctor/edit_doctor_profile.html", doctor=doctor)
