"""
Django ORM implementation of IMappingRepository.
"""
from typing import List, Optional
from apps.mappings.models import PatientDoctorMapping
from apps.mappings.interfaces import IMappingRepository


class DjangoMappingRepository(IMappingRepository):
    """Concrete repository using Django ORM with select_related for query optimization."""

    def assign(self, patient_id: int, doctor_id: int, notes: Optional[str] = None) -> PatientDoctorMapping:
        clean_notes = notes.strip() if isinstance(notes, str) and notes.strip() else None
        mapping = PatientDoctorMapping.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            notes=clean_notes
        )
        return PatientDoctorMapping.objects.select_related('patient', 'doctor').get(id=mapping.id)

    def get_by_id(self, mapping_id: int) -> Optional[PatientDoctorMapping]:
        try:
            return PatientDoctorMapping.objects.select_related('patient', 'doctor').get(id=mapping_id)
        except PatientDoctorMapping.DoesNotExist:
            return None

    def list_by_user(self, user_id: int) -> List[PatientDoctorMapping]:
        return list(
            PatientDoctorMapping.objects
            .filter(patient__created_by_id=user_id)
            .select_related('patient', 'doctor')
        )

    def get_by_patient(self, patient_id: int) -> List[PatientDoctorMapping]:
        return list(
            PatientDoctorMapping.objects
            .filter(patient_id=patient_id)
            .select_related('patient', 'doctor')
        )

    def exists(self, patient_id: int, doctor_id: int) -> bool:
        return PatientDoctorMapping.objects.filter(patient_id=patient_id, doctor_id=doctor_id).exists()

    def delete(self, mapping_id: int) -> bool:
        try:
            mapping = PatientDoctorMapping.objects.get(id=mapping_id)
            mapping.delete()
            return True
        except PatientDoctorMapping.DoesNotExist:
            return False
