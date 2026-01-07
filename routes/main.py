"""
Main navigation and dashboard routes for the EHR system.
"""

from flask import Blueprint, redirect, url_for, flash, render_template, session
from datetime import datetime
from models import (
    db,
    Doctor,
    Patient,
    LaboratoryResult,
    Appointment,
    RadiologyImaging
)
from utils.auth_decorators import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Redirect to login page if not authenticated."""
    if "doctor_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Display the main dashboard with recent data."""
    doctor_id = session.get("doctor_id")
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        flash("Doctor not found. Please log in again.", "error")
        return redirect(url_for("auth.logout"))

    try:
        lab_results = (
            db.session.query(LaboratoryResult, Patient)
            .join(Patient, LaboratoryResult.patient_id == Patient.id)
            .filter(Patient.doctor_id == doctor_id)
            .order_by(LaboratoryResult.date.desc())
            .limit(10)
            .all()
        )
    except Exception as e:
        print(f"Error fetching lab results: {e}")
        lab_results = []

    try:
        # Get upcoming appointments for this doctor
        appointments = (
            Appointment.query.filter_by(doctor_id=doctor_id)
            .order_by(Appointment.date.desc())
            .limit(10)
            .all()
        )
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        appointments = []

    return render_template(
        "main/dashboard.html",
        lab_results=lab_results,
        appointments=appointments,
        doctor=doctor,
    )


@main_bp.route("/about_us")
def about_us():
    """Display about us page with system statistics."""
    try:
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        total_lab_results = LaboratoryResult.query.count()
        total_imagings = RadiologyImaging.query.count()
        total_doctors = Doctor.query.count()

        system_stats = {
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "total_lab_results": total_lab_results,
            "total_imagings": total_imagings,
            "total_doctors": total_doctors,
        }

        return render_template(
            "main/about_us.html", system_stats=system_stats, datetime=datetime
        )

    except Exception as e:
        flash(f"Error loading about page: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))
