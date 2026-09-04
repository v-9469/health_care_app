"""
Django ORM implementation of IDoctorRepository.
"""
from typing import List, Optional
from django.db.models import Q
from apps.doctors.models import Doctor
from apps.doctors.interfaces import IDoctorRepository


class DjangoDoctorRepository(IDoctorRepository):
    """Concrete repository interacting with PostgreSQL via Django ORM."""

    def get_by_id(self, doctor_id: int) -> Optional[Doctor]:
        try:
            return Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[Doctor]:
        try:
            return Doctor.objects.get(email__iexact=email.strip())
        except Doctor.DoesNotExist:
            return None

    def list_all(self, specialization: Optional[str] = None, search: Optional[str] = None) -> List[Doctor]:
        queryset = Doctor.objects.all()

        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization.strip())

        if search:
            query = search.strip()
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(specialization__icontains=query) |
                Q(email__icontains=query)
            )

        return list(queryset)

    def create(self, name: str, specialization: str, contact_number: str, email: str, experience_years: int = 0) -> Doctor:
        return Doctor.objects.create(
            name=name.strip(),
            specialization=specialization.strip(),
            contact_number=contact_number.strip(),
            email=email.strip().lower(),
            experience_years=experience_years
        )

    def update(self, doctor_id: int, **data) -> Optional[Doctor]:
        doctor = self.get_by_id(doctor_id)
        if not doctor:
            return None

        for field, value in data.items():
            if hasattr(doctor, field) and field not in ('id', 'created_at', 'updated_at'):
                if isinstance(value, str):
                    value = value.strip()
                    if field == 'email':
                        value = value.lower()
                setattr(doctor, field, value)

        doctor.save()
        return doctor

    def delete(self, doctor_id: int) -> bool:
        doctor = self.get_by_id(doctor_id)
        if not doctor:
            return False
        doctor.delete()
        return True
