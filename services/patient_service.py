"""
Patient service layer for handling patient-related business logic.
"""

from datetime import datetime
from typing import Tuple, List, Optional
from models import (
    db,
    Patient,
    DemographicInfo,
    SocialHistory,
    GenderEnum,
    AlcoholConsumptionEnum,
    DrugUseEnum,
)
from flask import request, current_app


class PatientService:
    """Service class for patient-related operations."""

    @staticmethod
    def find_patient_by_id(patient_id: int, doctor_id: int) -> Optional[Patient]:
        """Find patient by ID and doctor ID."""
        return Patient.query.filter_by(id=patient_id, doctor_id=doctor_id).first()

    @staticmethod
    def parse_patient_form() -> Tuple[dict, List[str]]:
        """Parse and validate patient form data. Returns (data_dict, errors_list)."""
        first_name = request.form.get("first_name", "").strip().capitalize()
        last_name = request.form.get("last_name", "").strip().capitalize()
        email = request.form.get("email", "").strip().lower()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip().lower()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        address = request.form.get("address", "").strip()
        emergency_contact = request.form.get("emergency_contact", "").strip()
        smoking_status = request.form.get("smoking_status") is not None
        alcohol_use = request.form.get("alcohol_use", "").strip()
        drug_use = request.form.get("drug_use", "").strip()
        occupation = (
            request.form.get("occupation", "").strip().capitalize()
            if request.form.get("occupation")
            else ""
        )

        errors = []

        if not first_name:
            errors.append("First name is required")
        if not last_name:
            errors.append("Last name is required")
        if not date_of_birth:
            errors.append("Date of birth is required")
        if not gender:
            errors.append("Gender is required")
        if age and not age.isdigit():
            errors.append("Age must be a number")

        if date_of_birth:
            try:
                dob_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Invalid date format")
                dob_obj = None
        else:
            dob_obj = None

        patient_gender = None
        if gender:
            if gender not in current_app.config["GENDERS"]:
                errors.append("Invalid gender selection")
            else:
                patient_gender = GenderEnum(gender)

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email or None,
            "age": int(age) if age else None,
            "gender": patient_gender,
            "date_of_birth": dob_obj,
            "phone_number": phone_number or None,
            "address": address or None,
            "emergency_contact": emergency_contact or None,
            "smoking_status": smoking_status,
            "alcohol_use": AlcoholConsumptionEnum(alcohol_use) if alcohol_use else None,
            "drug_use": DrugUseEnum(drug_use) if drug_use else None,
            "occupation": occupation or None,
        }, errors

    @staticmethod
    def save_patient(
        patient: Optional[Patient] = None, doctor_id: int = None
    ) -> Tuple[Optional[Patient], List[str]]:
        """Create a new patient or update existing patient."""
        data, errors = PatientService.parse_patient_form()
        if errors:
            return None, errors

        try:
            if not patient:
                # Create new patient
                patient = Patient(
                    first_name=data["first_name"].capitalize(),
                    last_name=data["last_name"].capitalize(),
                    email=data["email"].lower() if data["email"] else None,
                    age=data["age"],
                    gender=data["gender"],
                    date_of_birth=data["date_of_birth"],
                    doctor_id=doctor_id,
                )
                db.session.add(patient)
                db.session.commit()  # commit first to get patient.id
            else:
                # Update existing patient
                patient.first_name = data["first_name"].capitalize()
                patient.last_name = data["last_name"].capitalize()
                patient.email = data["email"].lower() if data["email"] else None
                patient.age = data["age"]
                patient.gender = data["gender"]
                patient.date_of_birth = data["date_of_birth"]

            # Save demographics & social history
            PatientService.save_demographics(
                patient,
                data["phone_number"],
                data["address"],
                data["emergency_contact"],
            )
            PatientService.save_social_history(
                patient,
                data["smoking_status"],
                data["alcohol_use"],
                data["drug_use"],
                data["occupation"],
            )

            db.session.commit()
            return patient, []

        except Exception as e:
            db.session.rollback()
            return None, [str(e)]

    @staticmethod
    def save_demographics(
        patient: Patient, phone_number: str, address: str, emergency_contact: str
    ):
        """Save or update patient demographics."""
        if phone_number or address or emergency_contact:
            if patient.demographic_info:
                patient.demographic_info.phone_number = phone_number
                patient.demographic_info.address = (
                    address.capitalize() if address else None
                )
                patient.demographic_info.emergency_contact = emergency_contact
            else:
                patient.demographic_info = DemographicInfo(
                    patient_id=patient.id,
                    phone_number=phone_number,
                    address=address.capitalize() if address else None,
                    emergency_contact=emergency_contact,
                )

    @staticmethod
    def save_social_history(
        patient: Patient, smoking_status: bool, alcohol_use, drug_use, occupation: str
    ):
        """Save or update patient social history."""
        if patient.social_history:
            patient.social_history.smoking_status = smoking_status
            patient.social_history.alcohol_use = alcohol_use
            patient.social_history.drug_use = drug_use
            patient.social_history.occupation = (
                occupation.capitalize() if occupation else None
            )
        else:
            if smoking_status or alcohol_use or drug_use or occupation:
                patient.social_history = SocialHistory(
                    patient_id=patient.id,
                    smoking_status=smoking_status,
                    alcohol_use=alcohol_use,
                    drug_use=drug_use,
                    occupation=occupation.capitalize() if occupation else None,
                )
