"""
Doctor Domain Service with Dependency Injection.
"""
from typing import List, Dict, Any, Optional
from apps.doctors.interfaces import IDoctorRepository
from core.exceptions import (
    DuplicateResourceException,
    NotFoundException,
    ValidationException
)


class DoctorService:
    """
    Domain service implementing business rules for doctor management.
    Depends strictly on the IDoctorRepository abstraction.
    """

    def __init__(self, doctor_repo: IDoctorRepository):
        self.doctor_repo = doctor_repo

    def create_doctor(self, name: str, specialization: str, contact_number: str,
                      email: str, experience_years: int = 0) -> Any:
        """Adds a new doctor with unique email verification."""
        clean_name = name.strip() if name else ""
        clean_spec = specialization.strip() if specialization else ""
        clean_contact = contact_number.strip() if contact_number else ""
        clean_email = email.strip().lower() if email else ""

        if not clean_name or len(clean_name) < 2:
            raise ValidationException("Doctor name must be at least 2 characters long.")

        if not clean_spec:
            raise ValidationException("Doctor specialization is required.")

        if not clean_contact or len(clean_contact) < 5:
            raise ValidationException("A valid contact number is required.")

        if not clean_email or '@' not in clean_email:
            raise ValidationException("A valid professional email address is required.")

        if experience_years < 0:
            raise ValidationException("Experience years cannot be negative.")

        # Check email uniqueness
        existing_doctor = self.doctor_repo.get_by_email(clean_email)
        if existing_doctor:
            raise DuplicateResourceException("A doctor with this email address already exists.")

        return self.doctor_repo.create(
            name=clean_name,
            specialization=clean_spec,
            contact_number=clean_contact,
            email=clean_email,
            experience_years=experience_years
        )

    def list_doctors(self, specialization: Optional[str] = None, search: Optional[str] = None) -> List[Any]:
        """Retrieves all doctors with optional filters."""
        return self.doctor_repo.list_all(specialization=specialization, search=search)

    def get_doctor(self, doctor_id: int) -> Any:
        """Retrieves a single doctor by ID."""
        doctor = self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} was not found.")
        return doctor

    def update_doctor(self, doctor_id: int, update_data: Dict[str, Any]) -> Any:
        """Updates doctor details and validates email uniqueness."""
        doctor = self.get_doctor(doctor_id)

        if 'email' in update_data:
            clean_email = update_data['email'].strip().lower()
            if not clean_email or '@' not in clean_email:
                raise ValidationException("A valid email address is required.")

            existing_doctor = self.doctor_repo.get_by_email(clean_email)
            if existing_doctor and getattr(existing_doctor, 'id', None) != doctor_id:
                raise DuplicateResourceException("A doctor with this email address already exists.")

        if 'name' in update_data and len(update_data['name'].strip()) < 2:
            raise ValidationException("Doctor name must be at least 2 characters long.")

        if 'experience_years' in update_data and update_data['experience_years'] < 0:
            raise ValidationException("Experience years cannot be negative.")

        updated_doctor = self.doctor_repo.update(doctor_id, **update_data)
        if not updated_doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} was not found.")
        return updated_doctor

    def delete_doctor(self, doctor_id: int) -> bool:
        """Deletes a doctor record."""
        # Ensure doctor exists before deleting
        self.get_doctor(doctor_id)
        success = self.doctor_repo.delete(doctor_id)
        if not success:
            raise NotFoundException(f"Doctor with ID {doctor_id} was not found.")
        return True
