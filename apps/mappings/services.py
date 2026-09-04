"""
Patient-Doctor Mapping Domain Service with Dependency Injection.
"""
from typing import List, Any, Optional
from apps.mappings.interfaces import IMappingRepository
from apps.patients.interfaces import IPatientRepository
from apps.doctors.interfaces import IDoctorRepository
from core.exceptions import (
    NotFoundException,
    DuplicateResourceException,
    ValidationException
)


class MappingService:
    """
    Domain service orchestrating Patient-Doctor relational mapping operations.
    Enforces user-scoping on patients, ensures doctor validity, and prevents duplicate mappings.
    """

    def __init__(
        self,
        mapping_repo: IMappingRepository,
        patient_repo: IPatientRepository,
        doctor_repo: IDoctorRepository
    ):
        self.mapping_repo = mapping_repo
        self.patient_repo = patient_repo
        self.doctor_repo = doctor_repo

    def assign_doctor(
        self,
        user_id: int,
        patient_id: int,
        doctor_id: int,
        notes: Optional[str] = None
    ) -> Any:
        """
        Assigns a doctor to a patient owned by the authenticated user.
        Raises NotFoundException if the patient or doctor does not exist or if the patient is unauthorized.
        Raises DuplicateResourceException if the mapping already exists.
        """
        if not patient_id:
            raise ValidationException("patient_id is required.")
        if not doctor_id:
            raise ValidationException("doctor_id is required.")

        patient = self.patient_repo.get_by_id(patient_id=patient_id, user_id=user_id)
        if not patient:
            raise NotFoundException(f"Patient with ID {patient_id} was not found or unauthorized.")

        doctor = self.doctor_repo.get_by_id(doctor_id=doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} was not found.")

        if self.mapping_repo.exists(patient_id=patient_id, doctor_id=doctor_id):
            raise DuplicateResourceException(
                f"Doctor #{doctor_id} is already assigned to Patient #{patient_id}."
            )

        return self.mapping_repo.assign(
            patient_id=patient_id,
            doctor_id=doctor_id,
            notes=notes,
            patient=patient,
            doctor=doctor
        )

    def list_mappings(self, user_id: int) -> List[Any]:
        """
        Lists all patient-doctor mappings for patients owned by the specified user.
        """
        return self.mapping_repo.list_by_user(user_id=user_id)

    def get_doctors_for_patient(self, user_id: int, patient_id: int) -> List[Any]:
        """
        Retrieves all doctors assigned to a specific patient owned by the user.
        """
        patient = self.patient_repo.get_by_id(patient_id=patient_id, user_id=user_id)
        if not patient:
            raise NotFoundException(f"Patient with ID {patient_id} was not found or unauthorized.")

        return self.mapping_repo.get_by_patient(patient_id=patient_id)

    def delete_mapping(self, user_id: int, mapping_id: int) -> bool:
        """
        Removes a patient-doctor mapping if the patient is owned by the authenticated user.
        """
        mapping = self.mapping_repo.get_by_id(mapping_id=mapping_id)
        if not mapping:
            raise NotFoundException(f"Mapping with ID {mapping_id} was not found.")

        # Enforce patient ownership check
        patient = self.patient_repo.get_by_id(patient_id=mapping.patient_id, user_id=user_id)
        if not patient:
            raise NotFoundException(f"Mapping with ID {mapping_id} was not found or unauthorized.")

        success = self.mapping_repo.delete(mapping_id=mapping_id)
        if not success:
            raise NotFoundException(f"Mapping with ID {mapping_id} was not found.")

        return True
