"""
File handling utilities for the EHR system.
"""

import os
import uuid
from flask import current_app


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed. Return True if found, False otherwise."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def generate_unique_filename(filename: str) -> str | None:
    """Generate unique filename to prevent conflicts."""
    if filename == "":
        return None

    file_extension = ""
    if "." in filename:
        file_extension = "." + filename.rsplit(".", 1)[1].lower()

    unique_filename = str(uuid.uuid4()) + file_extension
    return unique_filename


def save_uploaded_file(file, patient_id: int) -> str | None:
    """Create patient-specific subdirectory and save uploaded file and return filename."""
    if file and allowed_file(file.filename):
        filename = generate_unique_filename(file.filename)
        if filename:
            patient_dir = os.path.join(
                current_app.config["UPLOAD_FOLDER"], f"patient_{patient_id}"
            )
            os.makedirs(patient_dir, exist_ok=True)

            filepath = os.path.join(patient_dir, filename)
            file.save(filepath)
            return f"patient_{patient_id}/{filename}"
    return None


def delete_image_file(image_filename: str) -> bool:
    """Delete image file from filesystem. Return True if deleted successfully,
    False otherwise."""
    if image_filename:
        try:
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], image_filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
    return False
