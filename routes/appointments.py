"""
Appointment management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from datetime import datetime
from models import db, Appointment, Patient, AppointmentStatusEnum, AppointmentTypeEnum
from utils.auth_decorators import login_required
from services.patient_service import PatientService

appointments_bp = Blueprint("appointments", __name__)


@appointments_bp.route("/view_appointments")
@login_required
def view_appointments():
    """Display all appointments."""
    doctor_id = session.get("doctor_id")

    try:
        # Get all appointments for this doctor
        appointments = (
            Appointment.query.filter_by(doctor_id=doctor_id)
            .join(Patient)
            .order_by(Appointment.date.desc())
            .all()
        )

        # Get statistics
        total_appointments = len(appointments)
        upcoming_appointments = len(
            [a for a in appointments if a.date > datetime.now()]
        )
        completed_appointments = len(
            [a for a in appointments if a.status == AppointmentStatusEnum.COMPLETED]
        )

        # Get appointments by status
        scheduled = len(
            [a for a in appointments if a.status == AppointmentStatusEnum.SCHEDULED]
        )
        cancelled = len(
            [a for a in appointments if a.status == AppointmentStatusEnum.CANCELLED]
        )
        no_show = len(
            [a for a in appointments if a.status == AppointmentStatusEnum.NO_SHOW]
        )

        stats = {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming_appointments,
            "completed_appointments": completed_appointments,
            "scheduled_appointments": scheduled,
            "cancelled_appointments": cancelled,
            "no_show_appointments": no_show,
        }

        return render_template(
            "appointment/appointments.html",
            appointments=appointments,
            stats=stats,
            datetime=datetime,
        )

    except Exception as e:
        flash(f"Error loading appointments: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@appointments_bp.route("/schedule_appointment", methods=["GET", "POST"])
@login_required
def schedule_appointment():
    """Schedule a new appointment."""
    doctor_id = session.get("doctor_id")

    if request.method == "POST":
        try:
            # Get form data
            patient_id = request.form.get("patient_id", "").strip()
            appointment_date = request.form.get("appointment_date", "").strip()
            appointment_time = request.form.get("appointment_time", "").strip()
            appointment_type = (
                request.form.get("appointment_type", "")
                .strip()
                .lower()
                .replace("-", "_")
            )
            notes = request.form.get("notes", "").strip()

            # Validation
            errors = []
            if not patient_id:
                errors.append("Please select a patient")
            if not appointment_date:
                errors.append("Appointment date is required")
            if not appointment_time:
                errors.append("Appointment time is required")

            # Check if patient belongs to this doctor
            if patient_id:
                patient = PatientService.find_patient_by_id(int(patient_id), doctor_id)
                if not patient:
                    errors.append("Invalid patient selection")

            if errors:
                for error in errors:
                    flash(error, "error")
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "appointment/schedule_appointment.html", patients=patients
                )

            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M"
            )

            # Check for existing appointment at same time
            existing_appointment = Appointment.query.filter_by(
                doctor_id=doctor_id, date=appointment_datetime
            ).first()

            if existing_appointment:
                flash("You already have an appointment at this date and time.", "error")
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "appointment/schedule_appointment.html", patients=patients
                )

            # Create new appointment
            new_appointment = Appointment(
                patient_id=int(patient_id),
                doctor_id=doctor_id,
                date=appointment_datetime,
                status=AppointmentStatusEnum.SCHEDULED,
                appointment_type=(
                    AppointmentTypeEnum(appointment_type) if appointment_type else None
                ),
                notes=notes if notes else None,
            )

            db.session.add(new_appointment)
            db.session.commit()

            patient = Patient.query.get(patient_id)
            flash(
                f"Appointment scheduled for {patient.first_name} {patient.last_name}!",
                "success",
            )
            flash(
                f'Date and time: {appointment_datetime.strftime("%Y-%m-%d at %H:%M")}',
                "info",
            )
            return redirect(url_for("main.dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error scheduling appointment: {str(e)}", "error")
            patients = (
                Patient.query.filter_by(doctor_id=doctor_id)
                .order_by(Patient.last_name)
                .all()
            )
            return render_template(
                "appointment/schedule_appointment.html", patients=patients
            )

    # Get patients for dropdown
    patients = (
        Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.last_name).all()
    )
    # Get pre-selected patient ID from URL parameter
    selected_patient_id = request.args.get("patient_id")
    return render_template(
        "appointment/schedule_appointment.html",
        patients=patients,
        selected_patient_id=selected_patient_id,
    )


@appointments_bp.route("/view_appointment/<int:appointment_id>")
@login_required
def view_appointment(appointment_id):
    """View a specific appointment."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the appointment and ensure it belongs to this doctor
        appointment = (
            Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id)
            .join(Patient)
            .first()
        )

        if not appointment:
            flash("Appointment not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        return render_template(
            "appointment/view_appointment.html",
            appointment=appointment,
            datetime=datetime,
        )

    except Exception as e:
        flash(f"Error loading appointment: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@appointments_bp.route(
    "/edit_appointment/<int:appointment_id>", methods=["GET", "POST"]
)
@login_required
def edit_appointment(appointment_id):
    """Edit a specific appointment."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the appointment and ensure it belongs to this doctor
        appointment = (
            Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id)
            .join(Patient)
            .first()
        )

        if not appointment:
            flash("Appointment not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":
            # Get form data
            appointment_date = request.form.get("appointment_date", "").strip()
            appointment_time = request.form.get("appointment_time", "").strip()
            status = request.form.get("status", "").strip().lower().replace("-", "_")
            appointment_type = (
                request.form.get("appointment_type", "")
                .strip()
                .lower()
                .replace("-", "_")
            )
            notes = request.form.get("notes", "").strip()

            # Validation
            errors = []
            if not appointment_date:
                errors.append("Appointment date is required")
            if not appointment_time:
                errors.append("Appointment time is required")
            if not status:
                errors.append("Status is required")

            if errors:
                for error in errors:
                    flash(error, "error")
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "appointment/edit_appointment.html",
                    appointment=appointment,
                    patients=patients,
                    datetime=datetime,
                )

            # Create new appointment datetime
            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M"
            )

            # Check for existing appointment at same time (excluding current appointment)
            existing_appointment = (
                Appointment.query.filter_by(
                    doctor_id=doctor_id, date=appointment_datetime
                )
                .filter(Appointment.id != appointment_id)
                .first()
            )

            if existing_appointment:
                flash(
                    "You already have another appointment at this date and time.",
                    "error",
                )
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "appointment/edit_appointment.html",
                    appointment=appointment,
                    patients=patients,
                    datetime=datetime,
                )

            # Update appointment
            appointment.date = appointment_datetime
            appointment.status = (
                AppointmentStatusEnum(status) if status else appointment.status
            )
            appointment.appointment_type = (
                AppointmentTypeEnum(appointment_type)
                if appointment_type
                else appointment.appointment_type
            )
            appointment.notes = notes if notes else None
            db.session.commit()

            flash(
                f"Appointment updated successfully for "
                f"{appointment.patient.first_name} {appointment.patient.last_name}!",
                "success",
            )
            return redirect(url_for("appointments.view_appointments"))

        # GET request - show edit form
        patients = (
            Patient.query.filter_by(doctor_id=doctor_id)
            .order_by(Patient.last_name)
            .all()
        )
        return render_template(
            "appointment/edit_appointment.html",
            appointment=appointment,
            patients=patients,
            datetime=datetime,
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error editing appointment: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@appointments_bp.route("/delete_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    """Delete a specific appointment."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the appointment and ensure it belongs to this doctor
        appointment = (
            Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id)
            .join(Patient)
            .first()
        )

        if not appointment:
            flash("Appointment not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        # Store patient name for flash message
        patient_name = (
            f"{appointment.patient.first_name} {appointment.patient.last_name}"
        )

        # Delete the appointment
        db.session.delete(appointment)
        db.session.commit()

        flash(
            f"Appointment for {patient_name} has been deleted successfully.", "success"
        )

        # Redirect based on source
        source = request.form.get("source", "")
        if source == "dashboard":
            return redirect(url_for("main.dashboard"))
        else:
            return redirect(url_for("appointments.view_appointments"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting appointment: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))
