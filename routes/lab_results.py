"""
Laboratory results management routes for the EHR system.
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from datetime import datetime
from models import db, LaboratoryResult, Patient, LabResultStatusEnum
from utils.auth_decorators import login_required
from services.patient_service import PatientService

lab_results_bp = Blueprint("lab_results", __name__)


@lab_results_bp.route("/view_lab_results")
@login_required
def view_lab_results():
    """Display all lab results."""
    doctor_id = session.get("doctor_id")

    try:
        # Get all lab results for patients of this doctor
        lab_results_query = (
            db.session.query(LaboratoryResult, Patient)
            .join(Patient, LaboratoryResult.patient_id == Patient.id)
            .filter(Patient.doctor_id == doctor_id)
            .order_by(LaboratoryResult.date.desc())
        )

        lab_results = lab_results_query.all()

        # Get statistics
        total_results = len(lab_results)
        recent_results = len(
            [lr for lr, p in lab_results if (datetime.now() - lr.date).days <= 7]
        )

        # Get unique test types
        test_types = set([lr.test_name for lr, p in lab_results])

        stats = {
            "total_results": total_results,
            "recent_results": recent_results,
            "test_types_count": len(test_types),
            "test_types": sorted(list(test_types)),
        }

        return render_template(
            "lab/lab_results.html",
            lab_results=lab_results,
            stats=stats,
            datetime=datetime,
        )

    except Exception as e:
        flash(f"Error loading lab results: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@lab_results_bp.route("/add_lab_result", methods=["GET", "POST"])
@login_required
def add_lab_result():
    """Add a new lab result."""
    doctor_id = session.get("doctor_id")

    if request.method == "POST":
        try:
            patient_id = request.form.get("patient_id", "").strip()
            test_name = request.form.get("test_name", "").strip()
            test_date = request.form.get("test_date", "").strip()
            result = request.form.get("result", "").strip()
            unit = request.form.get("unit", "").strip()
            reference_range = request.form.get("reference_range", "").strip()
            status = request.form.get("status", "").strip().lower()
            notes = request.form.get("notes", "").strip()

            errors = []
            if not patient_id:
                errors.append("Please select a patient")
            if not test_name:
                errors.append("Test name is required")
            if not result:
                errors.append("Result is required")
            if not test_date:
                errors.append("Test date is required")

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
                return render_template("lab/add_lab_result.html", patients=patients)

            # Create lab_test datetime
            try:
                # Try datetime-local format first (YYYY-MM-DDTHH:MM)
                test_datetime = datetime.strptime(test_date, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    # Try date-only format (YYYY-MM-DD)
                    test_datetime = datetime.strptime(test_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Invalid date format")
                    for error in errors:
                        flash(error, "error")
                    patients = (
                        Patient.query.filter_by(doctor_id=doctor_id)
                        .order_by(Patient.last_name)
                        .all()
                    )
                    return render_template("lab/add_lab_result.html", patients=patients)

            # Create new lab result
            new_lab_result = LaboratoryResult(
                patient_id=int(patient_id),
                test_name=test_name,
                date=test_datetime,
                result=result,
                unit=unit if unit else None,
                reference_range=reference_range if reference_range else None,
                status=LabResultStatusEnum(status) if status else None,
                notes=notes if notes else None,
            )

            db.session.add(new_lab_result)
            db.session.commit()

            patient = Patient.query.get(patient_id)
            flash(
                f"Lab result added for {patient.first_name} {patient.last_name}: {test_name}",
                "success",
            )
            return redirect(url_for("lab_results.view_lab_results"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding lab result: {str(e)}", "error")
            patients = (
                Patient.query.filter_by(doctor_id=doctor_id)
                .order_by(Patient.last_name)
                .all()
            )
            return render_template("lab/add_lab_result.html", patients=patients)

    # Get patients for dropdown
    patients = (
        Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.last_name).all()
    )
    # Get pre-selected patient ID from URL parameter
    selected_patient_id = request.args.get("patient_id")
    return render_template(
        "lab/add_lab_result.html",
        patients=patients,
        selected_patient_id=selected_patient_id,
    )


@lab_results_bp.route("/edit_lab_result/<int:lab_result_id>", methods=["GET", "POST"])
@login_required
def edit_lab_result(lab_result_id):
    """Edit a specific lab result."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the lab result and ensure it belongs to this doctor
        lab_result = (
            LaboratoryResult.query.filter_by(id=lab_result_id)
            .join(Patient)
            .filter(Patient.doctor_id == doctor_id)
            .first()
        )

        if not lab_result:
            flash("Lab result not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":
            test_name = request.form.get("test_name", "").strip()
            test_date = request.form.get("test_date", "").strip()
            result = request.form.get("result", "").strip()
            unit = request.form.get("unit", "").strip()
            reference_range = request.form.get("reference_range", "").strip()
            status = request.form.get("status", "").strip().lower()
            notes = request.form.get("notes", "").strip()

            errors = []
            if not test_name:
                errors.append("Test name is required")
            if not result:
                errors.append("Result is required")
            if not test_date:
                errors.append("Test date is required")

            if errors:
                for error in errors:
                    flash(error, "error")
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "lab/edit_lab_result.html",
                    lab_result=lab_result,
                    patients=patients,
                    datetime=datetime,
                )

            # Try datetime-local format first (YYYY-MM-DDTHH:MM)
            try:
                test_datetime = datetime.strptime(test_date, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    # Try date-only format (YYYY-MM-DD)
                    test_datetime = datetime.strptime(test_date, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format", "error")

            # Update lab result
            lab_result.test_name = test_name
            lab_result.date = test_datetime
            lab_result.result = result
            lab_result.unit = unit if unit else None
            lab_result.reference_range = reference_range if reference_range else None
            lab_result.status = LabResultStatusEnum(status) if status else None
            lab_result.notes = notes if notes else None

            db.session.commit()

            flash(
                f"Lab result for {lab_result.patient.first_name} "
                f"{lab_result.patient.last_name} updated successfully!",
                "success",
            )
            return redirect(url_for("lab_results.view_lab_results"))

        # GET request - show edit form
        patients = (
            Patient.query.filter_by(doctor_id=doctor_id)
            .order_by(Patient.last_name)
            .all()
        )
        return render_template(
            "lab/edit_lab_result.html",
            lab_result=lab_result,
            patients=patients,
            datetime=datetime,
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error editing lab result: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@lab_results_bp.route("/delete_lab_result/<int:lab_result_id>", methods=["POST"])
@login_required
def delete_lab_result(lab_result_id):
    """Delete a specific lab result."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the lab result and ensure it belongs to this doctor
        lab_result = (
            LaboratoryResult.query.filter_by(id=lab_result_id)
            .join(Patient)
            .filter(Patient.doctor_id == doctor_id)
            .first()
        )

        if not lab_result:
            flash("Lab result not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        # Store patient name for flash message
        patient_name = f"{lab_result.patient.first_name} {lab_result.patient.last_name}"
        test_name = lab_result.test_name

        # Delete the lab result
        db.session.delete(lab_result)
        db.session.commit()

        flash(
            f"Lab result '{test_name}' for {patient_name} has been deleted successfully.",
            "success",
        )

        # Redirect based on source
        source = request.form.get("source", "")
        if source == "dashboard":
            return redirect(url_for("main.dashboard"))
        else:
            return redirect(url_for("lab_results.view_lab_results"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting lab result: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))
