"""
Django ORM implementation of IPatientRepository.
"""
from typing import List, Optional
from django.db.models import Q
from apps.patients.models import Patient
from apps.patients.interfaces import IPatientRepository


class DjangoPatientRepository(IPatientRepository):
    """Concrete repository interacting with PostgreSQL via Django ORM."""

    def get_by_id(self, patient_id: int, user_id: Optional[int] = None) -> Optional[Patient]:
        try:
            queryset = Patient.objects.all()
            if user_id is not None:
                queryset = queryset.filter(created_by_id=user_id)
            return queryset.get(id=patient_id)
        except Patient.DoesNotExist:
            return None

    def list_by_user(self, user_id: int, search: Optional[str] = None) -> List[Patient]:
        queryset = Patient.objects.filter(created_by_id=user_id)

        if search:
            query = search.strip()
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(contact_number__icontains=query) |
                Q(email__icontains=query)
            )

        return list(queryset)

    def create(self, user_id: int, **data) -> Patient:
        return Patient.objects.create(
            created_by_id=user_id,
            name=data.get('name', '').strip(),
            age=data.get('age', 0),
            gender=data.get('gender', 'Male'),
            contact_number=data.get('contact_number', '').strip(),
            email=data.get('email', '').strip().lower() if data.get('email') else None,
            address=data.get('address', '').strip(),
            medical_history=data.get('medical_history', '').strip() if data.get('medical_history') else None
        )

    def update(self, patient_id: int, user_id: int, **data) -> Optional[Patient]:
        patient = self.get_by_id(patient_id, user_id)
        if not patient:
            return None

        for field, value in data.items():
            if hasattr(patient, field) and field not in ('id', 'created_by', 'created_at', 'updated_at'):
                if isinstance(value, str):
                    value = value.strip()
                    if field == 'email' and value:
                        value = value.lower()
                setattr(patient, field, value)

        patient.save()
        return patient

    def delete(self, patient_id: int, user_id: int) -> bool:
        patient = self.get_by_id(patient_id, user_id)
        if not patient:
            return False
        patient.delete()
        return True
