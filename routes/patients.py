"""
Patient management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from models import (
    db,
    Patient,
    GenderEnum,
    MedicalHistory,
    Allergy,
    Appointment,
    LaboratoryResult,
    RadiologyImaging,
    SocialHistory,
)
from utils.auth_decorators import login_required
from services.patient_service import PatientService
from datetime import date

patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/patients")
@login_required
def view_all_patients():
    """Display all patients in a table with statistics."""
    doctor_id = session.get("doctor_id")
    try:
        patients_query = Patient.query.filter_by(doctor_id=doctor_id).order_by(
            Patient.last_name, Patient.first_name
        )
        patients = patients_query.all()
        total_patients = len(patients)
        male_patients = sum(1 for p in patients if p.gender == GenderEnum.MALE)
        female_patients = sum(1 for p in patients if p.gender == GenderEnum.FEMALE)
        other_patients = total_patients - male_patients - female_patients
        current_date = date.today()
        age_groups = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}

        for patient in patients:
            if patient.date_of_birth:
                age = (current_date - patient.date_of_birth).days // 365
                if age <= 18:
                    age_groups["0-18"] += 1
                elif age <= 35:
                    age_groups["19-35"] += 1
                elif age <= 50:
                    age_groups["36-50"] += 1
                elif age <= 65:
                    age_groups["51-65"] += 1
                else:
                    age_groups["65+"] += 1

            # Get counts for each patient
            patient.appointment_count = Appointment.query.filter_by(
                patient_id=patient.id
            ).count()
            patient.lab_result_count = LaboratoryResult.query.filter_by(
                patient_id=patient.id
            ).count()
            patient.radiology_result_count = RadiologyImaging.query.filter_by(
                patient_id=patient.id
            ).count()
            patient.medical_history_count = MedicalHistory.query.filter_by(
                patient_id=patient.id
            ).count()

            # Get recent medical histories with allergy information
            patient.recent_medical_histories = (
                db.session.query(MedicalHistory, Allergy)
                .join(Allergy, MedicalHistory.allergy_id == Allergy.id)
                .filter(MedicalHistory.patient_id == patient.id)
                .order_by(MedicalHistory.date.desc())
                .limit(3)
                .all()
            )

        patients_with_history = sum(1 for p in patients if p.medical_history_count > 0)

        stats = {
            "total_patients": total_patients,
            "male_patients": male_patients,
            "female_patients": female_patients,
            "other_patients": other_patients,
            "age_groups": age_groups,
            "patients_with_history": patients_with_history,
        }

        return render_template("patient/patients.html", patients=patients, stats=stats)
    except Exception as e:
        flash(f"Error loading patients: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@patients_bp.route("/add_patient", methods=["GET", "POST"])
@login_required
def add_patient():
    """Add a new patient."""
    if request.method == "POST":
        doctor_id = session.get("doctor_id")
        patient, errors = PatientService.save_patient(doctor_id=doctor_id)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("patient/add_patient.html")
        flash(
            f"Patient {patient.first_name} {patient.last_name} added successfully!",
            "success",
        )
        return redirect(url_for("patients.view_all_patients"))
    return render_template("patient/add_patient.html")


@patients_bp.route("/patient/<int:patient_id>")
@login_required
def view_patient(patient_id):
    """Display detailed info for a single patient."""
    doctor_id = session.get("doctor_id")
    patient = PatientService.find_patient_by_id(patient_id, doctor_id)
    if not patient:
        flash("Patient not found or access denied.", "error")
        return redirect(url_for("patients.view_all_patients"))

    # Get related info
    appointments = (
        Appointment.query.filter_by(patient_id=patient.id)
        .order_by(Appointment.date.desc())
        .limit(5)
        .all()
    )
    lab_results = (
        LaboratoryResult.query.filter_by(patient_id=patient.id)
        .order_by(LaboratoryResult.date.desc())
        .limit(5)
        .all()
    )
    radiology_imaging = (
        RadiologyImaging.query.filter_by(patient_id=patient.id)
        .order_by(RadiologyImaging.date.desc())
        .limit(5)
        .all()
    )
    medical_histories = (
        db.session.query(MedicalHistory, Allergy)
        .join(Allergy, MedicalHistory.allergy_id == Allergy.id)
        .filter(MedicalHistory.patient_id == patient.id)
        .order_by(MedicalHistory.date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "patient/view_patient.html",
        patient=patient,
        appointments=appointments,
        lab_results=lab_results,
        radiology_imaging=radiology_imaging,
        medical_histories=medical_histories,
    )


@patients_bp.route("/edit_patient/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Edit an existing patient."""
    doctor_id = session.get("doctor_id")
    patient = PatientService.find_patient_by_id(patient_id, doctor_id)
    if not patient:
        flash("Patient not found or access denied.", "error")
        return redirect(url_for("patients.view_all_patients"))

    if request.method == "POST":
        updated_patient, errors = PatientService.save_patient(patient)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("patient/edit_patient.html", patient=patient)
        flash(
            f"Patient {updated_patient.first_name} {updated_patient.last_name} updated successfully!",
            "success",
        )
        return redirect(url_for("patients.view_patient", patient_id=patient.id))

    return render_template("patient/edit_patient.html", patient=patient)


@patients_bp.route("/delete_patient/<int:patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """Delete patient and all related records."""
    doctor_id = session.get("doctor_id")
    patient = PatientService.find_patient_by_id(patient_id, doctor_id)
    if not patient:
        flash("Patient not found or access denied.", "error")
        return redirect(url_for("patients.view_all_patients"))

    try:
        patient_name = f"{patient.first_name} {patient.last_name}"

        # Delete related records first to avoid foreign key constraints
        Appointment.query.filter_by(patient_id=patient.id).delete()
        LaboratoryResult.query.filter_by(patient_id=patient.id).delete()
        MedicalHistory.query.filter_by(patient_id=patient.id).delete()
        SocialHistory.query.filter_by(patient_id=patient.id).delete()
        RadiologyImaging.query.filter_by(patient_id=patient.id).delete()

        # Delete patient
        db.session.delete(patient)
        db.session.commit()

        flash(
            f"Patient {patient_name} and all related records deleted successfully!",
            "success",
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting patient: {str(e)}", "error")

    return redirect(url_for("patients.view_all_patients"))
