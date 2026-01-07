"""
Medical history management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from datetime import datetime
from models import db, Patient, MedicalHistory, Allergy
from utils.auth_decorators import login_required
from services.patient_service import PatientService

medical_history_bp = Blueprint("medical_history", __name__)


@medical_history_bp.route("/add_medical_history", methods=["GET", "POST"])
@login_required
def add_medical_history():
    """Add medical history entry for a patient."""
    doctor_id = session.get("doctor_id")

    if request.method == "POST":
        try:
            patient_id = request.form.get("patient_id", "").strip()
            allergy_name = request.form.get("allergy_name", "").strip()
            description = request.form.get("description", "").strip()
            history_date = request.form.get("history_date", "").strip()

            errors = []
            if not patient_id:
                errors.append("Please select a patient")
            if not allergy_name:
                errors.append("Please enter an allergy or condition")
            if not description:
                errors.append("Description is required")
            if not history_date:
                errors.append("Date is required")

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
                allergies = Allergy.query.order_by(Allergy.name).all()
                return render_template(
                    "medical_history/add_medical_history.html",
                    patients=patients,
                    allergies=allergies,
                )

            # Parse date
            history_datetime = datetime.strptime(history_date, "%Y-%m-%d")

            # Handle allergy: find existing or create new one
            allergy = Allergy.query.filter_by(name=allergy_name).first()
            if not allergy:
                # Create new allergy
                allergy = Allergy(name=allergy_name, description="")
                db.session.add(allergy)
                db.session.flush()  # Get the ID without committing
                flash(
                    f"New allergy/condition '{allergy_name}' added to the system.",
                    "info",
                )

            # Create new medical history entry
            new_history = MedicalHistory(
                patient_id=int(patient_id),
                allergy_id=allergy.id,
                description=description,
                date=history_datetime,
            )

            db.session.add(new_history)
            db.session.commit()

            patient = Patient.query.get(patient_id)
            flash(
                f"Medical history added for {patient.first_name} {patient.last_name}!",
                "success",
            )
            return redirect(url_for("patients.view_all_patients"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding medical history: {str(e)}", "error")
            patients = (
                Patient.query.filter_by(doctor_id=doctor_id)
                .order_by(Patient.last_name)
                .all()
            )
            allergies = Allergy.query.order_by(Allergy.name).all()
            return render_template(
                "medical_history/add_medical_history.html",
                patients=patients,
                allergies=allergies,
            )

    # Get patients and allergies for dropdowns
    patients = (
        Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.last_name).all()
    )

    allergies = Allergy.query.order_by(Allergy.name).all()

    # If no allergies exist, create common ones
    if not allergies:
        try:
            common_allergies = [
                (
                    "Penicillin",
                    "Antibiotic allergy - can cause rash, hives, or anaphylaxis",
                ),
                (
                    "Peanuts",
                    "Food allergy - can cause severe reactions, requires avoidance",
                ),
                ("Shellfish", "Food allergy - can cause mild to severe reactions"),
                ("Dust Mites", "Environmental allergy - causes respiratory symptoms"),
                ("Pollen", "Seasonal allergy - causes hay fever symptoms"),
                ("Latex", "Contact allergy - causes skin and systemic reactions"),
                ("Sulfa Drugs", "Medication allergy - can cause skin rashes and fever"),
                (
                    "Aspirin",
                    "Medication allergy - causes respiratory or skin reactions",
                ),
                ("Eggs", "Food allergy - common in children, various symptoms"),
                ("Dairy/Milk", "Food allergy - causes digestive and skin reactions"),
                ("Other", "For allergies not listed above - specify in description"),
            ]

            for name, description in common_allergies:
                allergy = Allergy(name=name, description=description)
                db.session.add(allergy)

            db.session.commit()
            allergies = Allergy.query.order_by(Allergy.name).all()
            flash("Common allergies have been added to the system.", "info")

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating allergies: {str(e)}", "error")

    # Get pre-selected patient ID from URL parameter
    selected_patient_id = request.args.get("patient_id")
    return render_template(
        "medical_history/add_medical_history.html",
        patients=patients,
        allergies=allergies,
        selected_patient_id=selected_patient_id,
    )


@medical_history_bp.route(
    "/edit_medical_history/<int:medical_history_id>", methods=["GET", "POST"]
)
@login_required
def edit_medical_history(medical_history_id):
    """Edit an existing medical history entry."""
    doctor_id = session.get("doctor_id")

    # Get the medical history record and verify ownership
    medical_history = (
        db.session.query(MedicalHistory, Allergy)
        .join(Allergy, MedicalHistory.allergy_id == Allergy.id)
        .join(Patient, MedicalHistory.patient_id == Patient.id)
        .filter(MedicalHistory.id == medical_history_id, Patient.doctor_id == doctor_id)
        .first()
    )

    if not medical_history:
        flash("Medical history record not found or access denied.", "error")
        return redirect(url_for("patients.view_all_patients"))

    history_record, allergy_record = medical_history

    if request.method == "POST":
        try:
            patient_id = request.form.get("patient_id", "").strip()
            allergy_name = request.form.get("allergy_name", "").strip()
            description = request.form.get("description", "").strip()
            history_date = request.form.get("history_date", "").strip()

            errors = []
            if not patient_id:
                errors.append("Please select a patient")
            if not allergy_name:
                errors.append("Please enter an allergy or condition")
            if not description:
                errors.append("Description is required")
            if not history_date:
                errors.append("Date is required")

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
                allergies = Allergy.query.order_by(Allergy.name).all()
                return render_template(
                    "medical_history/edit_medical_history.html",
                    medical_history=history_record,
                    allergy=allergy_record,
                    patients=patients,
                    allergies=allergies,
                )

            # Parse date
            history_datetime = datetime.strptime(history_date, "%Y-%m-%d")

            # Handle allergy: find existing or create new one
            allergy = Allergy.query.filter_by(name=allergy_name).first()
            if not allergy:
                # Create new allergy
                allergy = Allergy(name=allergy_name, description="")
                db.session.add(allergy)
                db.session.flush()  # Get the ID without committing
                flash(
                    f"New allergy/condition '{allergy_name}' added to the system.",
                    "info",
                )

            # Update medical history entry
            history_record.patient_id = int(patient_id)
            history_record.allergy_id = allergy.id
            history_record.description = description
            history_record.date = history_datetime

            db.session.commit()

            patient = Patient.query.get(patient_id)
            flash(
                f"Medical history updated for {patient.first_name} {patient.last_name}!",
                "success",
            )
            return redirect(url_for("patients.view_patient", patient_id=patient_id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating medical history: {str(e)}", "error")
            patients = (
                Patient.query.filter_by(doctor_id=doctor_id)
                .order_by(Patient.last_name)
                .all()
            )
            allergies = Allergy.query.order_by(Allergy.name).all()
            return render_template(
                "medical_history/edit_medical_history.html",
                medical_history=history_record,
                allergy=allergy_record,
                patients=patients,
                allergies=allergies,
            )

    # GET request - display form with existing data
    patients = (
        Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.last_name).all()
    )
    allergies = Allergy.query.order_by(Allergy.name).all()

    return render_template(
        "medical_history/edit_medical_history.html",
        medical_history=history_record,
        allergy=allergy_record,
        patients=patients,
        allergies=allergies,
    )


@medical_history_bp.route(
    "/delete_medical_history/<int:medical_history_id>", methods=["POST"]
)
@login_required
def delete_medical_history(medical_history_id):
    """Delete a medical history entry."""
    doctor_id = session.get("doctor_id")

    # Get the medical history record and verify ownership
    medical_history = (
        db.session.query(MedicalHistory, Allergy, Patient)
        .join(Allergy, MedicalHistory.allergy_id == Allergy.id)
        .join(Patient, MedicalHistory.patient_id == Patient.id)
        .filter(MedicalHistory.id == medical_history_id, Patient.doctor_id == doctor_id)
        .first()
    )

    if not medical_history:
        flash("Medical history record not found or access denied.", "error")
        return redirect(url_for("patients.view_all_patients"))

    history_record, allergy_record, patient_record = medical_history

    try:
        # Store patient info for redirect
        patient_id = history_record.patient_id
        patient_name = f"{patient_record.first_name} {patient_record.last_name}"
        allergy_name = allergy_record.name

        # Delete the medical history record
        db.session.delete(history_record)
        db.session.commit()

        flash(
            f"Medical history record '{allergy_name}' deleted for {patient_name}.",
            "success",
        )
        return redirect(url_for("patients.view_patient", patient_id=patient_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting medical history: {str(e)}", "error")
        return redirect(
            url_for("patients.view_patient", patient_id=history_record.patient_id)
        )
