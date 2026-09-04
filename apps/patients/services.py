"""
Patient Domain Service with Dependency Injection.
"""
from typing import List, Dict, Any, Optional
from apps.patients.interfaces import IPatientRepository
from core.exceptions import (
    NotFoundException,
    ValidationException
)


class PatientService:
    """
    Domain service implementing business rules and scoping for patient management.
    Depends strictly on the IPatientRepository abstraction.
    """

    VALID_GENDERS = {'Male', 'Female', 'Other'}

    def __init__(self, patient_repo: IPatientRepository):
        self.patient_repo = patient_repo

    def create_patient(self, user_id: int, data: Dict[str, Any]) -> Any:
        """Adds a new patient under the authenticated user's scope."""
        name = data.get('name', '').strip() if data.get('name') else ""
        age = data.get('age')
        gender = data.get('gender', '').strip() if data.get('gender') else ""
        contact_number = data.get('contact_number', '').strip() if data.get('contact_number') else ""
        email = data.get('email', '').strip().lower() if data.get('email') else None
        address = data.get('address', '').strip() if data.get('address') else ""

        if not name or len(name) < 2:
            raise ValidationException("Patient name must be at least 2 characters long.")

        if age is None or not isinstance(age, int) or age < 0 or age > 150:
            raise ValidationException("Age must be a positive integer between 0 and 150.")

        if gender not in self.VALID_GENDERS:
            raise ValidationException(f"Gender must be one of {list(self.VALID_GENDERS)}.")

        if not contact_number or len(contact_number) < 5:
            raise ValidationException("A valid contact phone number is required.")

        if email and '@' not in email:
            raise ValidationException("A valid email address is required if provided.")

        if not address:
            raise ValidationException("Residential address is required.")

        return self.patient_repo.create(
            user_id=user_id,
            name=name,
            age=age,
            gender=gender,
            contact_number=contact_number,
            email=email,
            address=address,
            medical_history=data.get('medical_history')
        )

    def list_patients(self, user_id: int, search: Optional[str] = None) -> List[Any]:
        """Retrieves all patients created by the specified user."""
        return self.patient_repo.list_by_user(user_id=user_id, search=search)

    def get_patient(self, patient_id: int, user_id: int) -> Any:
        """Retrieves a single patient ensuring ownership scoping."""
        patient = self.patient_repo.get_by_id(patient_id=patient_id, user_id=user_id)
        if not patient:
            raise NotFoundException(f"Patient with ID {patient_id} was not found or unauthorized.")
        return patient

    def update_patient(self, patient_id: int, user_id: int, update_data: Dict[str, Any]) -> Any:
        """Updates patient details for an owned record."""
        self.get_patient(patient_id=patient_id, user_id=user_id)

        if 'name' in update_data and len(update_data['name'].strip()) < 2:
            raise ValidationException("Patient name must be at least 2 characters long.")

        if 'age' in update_data:
            age = update_data['age']
            if not isinstance(age, int) or age < 0 or age > 150:
                raise ValidationException("Age must be a positive integer between 0 and 150.")

        if 'gender' in update_data and update_data['gender'] not in self.VALID_GENDERS:
            raise ValidationException(f"Gender must be one of {list(self.VALID_GENDERS)}.")

        if 'contact_number' in update_data and len(update_data['contact_number'].strip()) < 5:
            raise ValidationException("A valid contact phone number is required.")

        if 'email' in update_data and update_data['email']:
            if '@' not in update_data['email']:
                raise ValidationException("A valid email address is required if provided.")

        updated_patient = self.patient_repo.update(patient_id=patient_id, user_id=user_id, **update_data)
        if not updated_patient:
            raise NotFoundException(f"Patient with ID {patient_id} was not found.")
        return updated_patient

    def delete_patient(self, patient_id: int, user_id: int) -> bool:
        """Deletes a patient record if owned by the user."""
        self.get_patient(patient_id=patient_id, user_id=user_id)
        success = self.patient_repo.delete(patient_id=patient_id, user_id=user_id)
        if not success:
            raise NotFoundException(f"Patient with ID {patient_id} was not found.")
        return True
