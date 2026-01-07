"""
Radiology imaging management routes for the EHR system.
"""

from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    session,
    send_from_directory,
    current_app,
)
from datetime import datetime
import os
from models import db, RadiologyImaging, Patient
from utils.auth_decorators import login_required
from utils.file_handlers import save_uploaded_file, allowed_file, delete_image_file
from services.patient_service import PatientService

radiology_bp = Blueprint("radiology", __name__)


@radiology_bp.route("/view_radiology_imaging")
@login_required
def view_radiology_imaging():
    """View all radiology imaging records."""
    doctor_id = session.get("doctor_id")

    # Get search parameters
    search_patient = request.args.get("search_patient", "").strip()
    search_imaging = request.args.get("search_imaging", "").strip()

    query = (
        db.session.query(RadiologyImaging)
        .join(Patient)
        .filter(Patient.doctor_id == doctor_id)
    )

    # Apply filters
    if search_patient:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f"%{search_patient}%"),
                Patient.last_name.ilike(f"%{search_patient}%"),
            )
        )

    if search_imaging:
        query = query.filter(RadiologyImaging.name.ilike(f"%{search_imaging}%"))

    # Execute query and order results
    radiology_imaging = query.order_by(RadiologyImaging.date.desc()).all()

    return render_template(
        "radiology/view_radiology_imaging.html",
        radiology_imaging=radiology_imaging,
        search_patient=search_patient,
        search_imaging=search_imaging,
    )


@radiology_bp.route("/add_radiology_imaging", methods=["GET", "POST"])
@login_required
def add_radiology_imaging():
    """Add new radiology imaging record."""
    doctor_id = session.get("doctor_id")

    if request.method == "POST":
        try:
            patient_id = request.form.get("patient_id", "").strip()
            imaging_name = request.form.get("imaging_name", "").strip()
            imaging_date = request.form.get("imaging_date", "").strip()

            errors = []
            if not patient_id:
                errors.append("Please select a patient")
            if not imaging_name:
                errors.append("Imaging name is required")
            if not imaging_date:
                errors.append("Imaging date is required")

            # Handle file upload
            image_file = request.files.get("image_file")
            if image_file and image_file.filename != "":
                if not allowed_file(image_file.filename):
                    errors.append(
                        "Invalid file type. Allowed formats: PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM"
                    )

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
                    "radiology/add_radiology_imaging.html", patients=patients
                )

            # Create imaging datetime
            try:
                # Try datetime-local format first (YYYY-MM-DDTHH:MM)
                imaging_datetime = datetime.strptime(imaging_date, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    # Try date-only format (YYYY-MM-DD)
                    imaging_datetime = datetime.strptime(imaging_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Invalid date format")
                    for error in errors:
                        flash(error, "error")
                    patients = (
                        Patient.query.filter_by(doctor_id=doctor_id)
                        .order_by(Patient.last_name)
                        .all()
                    )
                    return render_template(
                        "radiology/add_radiology_imaging.html", patients=patients
                    )
            # Handle file upload if present
            image_filename = None
            if image_file and image_file.filename != "":
                image_filename = save_uploaded_file(image_file, int(patient_id))
                if not image_filename:
                    errors.append("Failed to save uploaded image")
                    for error in errors:
                        flash(error, "error")
                    patients = (
                        Patient.query.filter_by(doctor_id=doctor_id)
                        .order_by(Patient.last_name)
                        .all()
                    )
                    return render_template(
                        "radiology/add_radiology_imaging.html", patients=patients
                    )

            # Create new radiology imaging record
            new_imaging = RadiologyImaging(
                patient_id=int(patient_id),
                name=imaging_name,
                date=imaging_datetime,
                image_filename=image_filename,
            )

            db.session.add(new_imaging)
            db.session.commit()

            patient = Patient.query.get(patient_id)
            flash(
                f"Radiology imaging added for {patient.first_name} {patient.last_name}: {imaging_name}",
                "success",
            )
            return redirect(url_for("radiology.view_radiology_imaging"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding radiology imaging: {str(e)}", "error")

    # GET request - show form
    patients = (
        Patient.query.filter_by(doctor_id=doctor_id).order_by(Patient.last_name).all()
    )
    selected_patient_id = request.args.get("patient_id", "")
    return render_template(
        "radiology/add_radiology_imaging.html",
        patients=patients,
        selected_patient_id=selected_patient_id,
    )


@radiology_bp.route("/radiology_image/<path:filename>")
@login_required
def radiology_image(filename):
    """Serve radiology images securely."""
    doctor_id = session.get("doctor_id")

    # Extract patient ID from filename path (format: patient_X/filename.ext)
    try:
        if "/" in filename:
            patient_folder, image_name = filename.split("/", 1)
            patient_id = int(patient_folder.replace("patient_", ""))

            # Verify that this patient belongs to the logged-in doctor
            patient = PatientService.find_patient_by_id(patient_id, doctor_id)
            if not patient:
                flash("Access denied to this image.", "error")
                return redirect(url_for("radiology.view_radiology_imaging"))

            # Serve the file
            return send_from_directory(
                os.path.join(current_app.config["UPLOAD_FOLDER"], patient_folder),
                image_name,
                )
        else:
            flash("Invalid image path.", "error")
            return redirect(url_for("radiology.view_radiology_imaging"))

    except (ValueError, IndexError):
        flash("Invalid image path.", "error")
        return redirect(url_for("radiology.view_radiology_imaging"))


@radiology_bp.route("/edit_radiology_imaging/<int:imaging_id>", methods=["GET", "POST"])
@login_required
def edit_radiology_imaging(imaging_id):
    """Edit a specific radiology imaging record."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the imaging record and ensure it belongs to this doctor
        imaging_record = (
            RadiologyImaging.query.filter_by(id=imaging_id)
            .join(Patient)
            .filter(Patient.doctor_id == doctor_id)
            .first()
        )

        if not imaging_record:
            flash("Imaging record not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":
            imaging_name = request.form.get("imaging_name", "").strip()
            imaging_date = request.form.get("imaging_date", "").strip()

            errors = []
            if not imaging_name:
                errors.append("Imaging name is required")
            if not imaging_date:
                errors.append("Imaging date is required")

            if errors:
                for error in errors:
                    flash(error, "error")
                patients = (
                    Patient.query.filter_by(doctor_id=doctor_id)
                    .order_by(Patient.last_name)
                    .all()
                )
                return render_template(
                    "radiology/edit_radiology_imaging.html",
                    imaging_record=imaging_record,
                    patients=patients,
                    datetime=datetime,
                )

            # Update imaging record
            imaging_record.name = imaging_name
            try:
                # Try datetime-local format first (YYYY-MM-DDTHH:MM)
                imaging_record.date = datetime.strptime(imaging_date, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    # Try date-only format (YYYY-MM-DD)
                    imaging_record.date = datetime.strptime(imaging_date, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format", "error")
                    patients = (
                        Patient.query.filter_by(doctor_id=doctor_id)
                        .order_by(Patient.last_name)
                        .all()
                    )
                    return render_template(
                        "radiology/edit_radiology_imaging.html",
                        imaging_record=imaging_record,
                        patients=patients,
                        datetime=datetime,
                    )

            db.session.commit()

            flash(
                f"Radiology imaging record for {imaging_record.patient.first_name} "
                f"{imaging_record.patient.last_name} updated successfully!",
                "success",
            )
            return redirect(url_for("radiology.view_radiology_imaging"))

        # GET request - show edit form
        patients = (
            Patient.query.filter_by(doctor_id=doctor_id)
            .order_by(Patient.last_name)
            .all()
        )
        return render_template(
            "radiology/edit_radiology_imaging.html",
            imaging_record=imaging_record,
            patients=patients,
            datetime=datetime,
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error editing radiology record: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))


@radiology_bp.route("/delete_radiology_imaging/<int:imaging_id>", methods=["POST"])
@login_required
def delete_radiology_imaging(imaging_id):
    """Delete a specific radiology imaging record."""
    doctor_id = session.get("doctor_id")

    try:
        # Get the imaging record and ensure it belongs to this doctor
        imaging_record = (
            RadiologyImaging.query.filter_by(id=imaging_id)
            .join(Patient)
            .filter(Patient.doctor_id == doctor_id)
            .first()
        )

        if not imaging_record:
            flash("Imaging record not found or access denied.", "error")
            return redirect(url_for("main.dashboard"))

        # Store patient name for flash message
        patient_name = (
            f"{imaging_record.patient.first_name} "
            f"{imaging_record.patient.last_name}"
        )
        imaging_name = imaging_record.name

        # Delete associated image file if it exists
        if imaging_record.image_filename:
            if delete_image_file(imaging_record.image_filename):
                # Delete the imaging record
                db.session.delete(imaging_record)
                db.session.commit()
                flash(
                    f"Radiology imaging record '{imaging_name}' "
                    f"for {patient_name} has been deleted successfully.",
                    "success",
                )
            else:
                flash(
                    "Failed to delete associated image file. Record not deleted.",
                    "error",
                )
                return redirect(url_for("radiology.view_radiology_imaging"))

        # Redirect based on source
        source = request.form.get("source", "")
        if source == "dashboard":
            return redirect(url_for("main.dashboard"))
        else:
            return redirect(url_for("radiology.view_radiology_imaging"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting radiology record: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))
