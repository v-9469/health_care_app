"""
In-memory Mock Repositories for ultra-fast, zero-database Pytest execution.
Adheres strictly to domain repository interfaces.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime


class MockUser:
    """Mock User entity."""
    def __init__(self, id: int, name: str, email: str, password: str, is_active: bool = True, is_staff: bool = False):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_authenticated = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def check_password(self, raw_password: str) -> bool:
        # Check raw or mocked match
        return self.password == raw_password or self.password.startswith("pbkdf2_") or self.password.startswith("hashed_")

    def set_password(self, raw_password: str):
        self.password = f"hashed_{raw_password}"


class MockUserRepository:
    """In-memory User repository simulating DB operations."""
    def __init__(self):
        self.users: Dict[int, MockUser] = {}
        self._next_id = 1

    def get_by_email(self, email: str) -> Optional[MockUser]:
        return next((u for u in self.users.values() if u.email.lower() == email.lower()), None)

    def get_by_id(self, user_id: int) -> Optional[MockUser]:
        return self.users.get(user_id)

    def create(self, name: str, email: str, password: str, **kwargs) -> MockUser:
        user = MockUser(
            id=self._next_id,
            name=name,
            email=email,
            password=password,
            is_active=kwargs.get('is_active', True),
            is_staff=kwargs.get('is_staff', False)
        )
        self.users[self._next_id] = user
        self._next_id += 1
        return user


class MockPatient:
    """Mock Patient entity."""
    def __init__(self, id: int, created_by_id: int, name: str, age: int, gender: str, contact_number: str,
                 email: Optional[str] = None, address: str = "", medical_history: Optional[str] = None):
        self.id = id
        self.created_by_id = created_by_id
        self.name = name
        self.age = age
        self.gender = gender
        self.contact_number = contact_number
        self.email = email
        self.address = address
        self.medical_history = medical_history
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class MockPatientRepository:
    """In-memory Patient repository."""
    def __init__(self):
        self.patients: Dict[int, MockPatient] = {}
        self._next_id = 1

    def get_by_id(self, patient_id: int, user_id: Optional[int] = None) -> Optional[MockPatient]:
        patient = self.patients.get(patient_id)
        if patient and user_id is not None and patient.created_by_id != user_id:
            return None
        return patient

    def list_by_user(self, user_id: int, search: Optional[str] = None) -> List[MockPatient]:
        results = [p for p in self.patients.values() if p.created_by_id == user_id]
        if search:
            query = search.strip().lower()
            results = [
                p for p in results
                if query in p.name.lower() or query in p.contact_number.lower() or (p.email and query in p.email.lower())
            ]
        return results

    def create(self, user_id: int, **data) -> MockPatient:
        patient = MockPatient(
            id=self._next_id,
            created_by_id=user_id,
            name=data.get('name', ''),
            age=data.get('age', 0),
            gender=data.get('gender', 'M'),
            contact_number=data.get('contact_number', ''),
            email=data.get('email'),
            address=data.get('address', ''),
            medical_history=data.get('medical_history')
        )
        self.patients[self._next_id] = patient
        self._next_id += 1
        return patient

    def update(self, patient_id: int, user_id: int, **data) -> Optional[MockPatient]:
        patient = self.get_by_id(patient_id, user_id)
        if not patient:
            return None
        for key, value in data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        patient.updated_at = datetime.utcnow()
        return patient

    def delete(self, patient_id: int, user_id: int) -> bool:
        if patient_id in self.patients and self.patients[patient_id].created_by_id == user_id:
            del self.patients[patient_id]
            return True
        return False


class MockDoctor:
    """Mock Doctor entity."""
    def __init__(self, id: int, name: str, specialization: str, contact_number: str,
                 email: str, experience_years: int = 0):
        self.id = id
        self.name = name
        self.specialization = specialization
        self.contact_number = contact_number
        self.email = email
        self.experience_years = experience_years
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class MockDoctorRepository:
    """In-memory Doctor repository."""
    def __init__(self):
        self.doctors: Dict[int, MockDoctor] = {}
        self._next_id = 1

    def get_by_id(self, doctor_id: int) -> Optional[MockDoctor]:
        return self.doctors.get(doctor_id)

    def get_by_email(self, email: str) -> Optional[MockDoctor]:
        return next((d for d in self.doctors.values() if d.email.lower() == email.lower()), None)

    def list_all(self, specialization: Optional[str] = None, search: Optional[str] = None) -> List[MockDoctor]:
        results = list(self.doctors.values())
        if specialization:
            results = [d for d in results if specialization.lower() in d.specialization.lower()]
        if search:
            results = [d for d in results if search.lower() in d.name.lower() or search.lower() in d.specialization.lower()]
        return results

    def create(self, **data) -> MockDoctor:
        doctor = MockDoctor(
            id=self._next_id,
            name=data.get('name', ''),
            specialization=data.get('specialization', ''),
            contact_number=data.get('contact_number', ''),
            email=data.get('email', ''),
            experience_years=data.get('experience_years', 0)
        )
        self.doctors[self._next_id] = doctor
        self._next_id += 1
        return doctor

    def update(self, doctor_id: int, **data) -> Optional[MockDoctor]:
        doctor = self.get_by_id(doctor_id)
        if not doctor:
            return None
        for key, value in data.items():
            if hasattr(doctor, key):
                setattr(doctor, key, value)
        doctor.updated_at = datetime.utcnow()
        return doctor

    def delete(self, doctor_id: int) -> bool:
        if doctor_id in self.doctors:
            del self.doctors[doctor_id]
            return True
        return False


class MockMapping:
    """Mock Patient-Doctor Mapping entity."""
    def __init__(self, id: int, patient_id: int, doctor_id: int, notes: Optional[str] = None,
                 patient: Optional[MockPatient] = None, doctor: Optional[MockDoctor] = None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.notes = notes
        self.patient = patient
        self.doctor = doctor
        self.assigned_date = datetime.utcnow()


class MockMappingRepository:
    """In-memory Patient-Doctor Mapping repository."""
    def __init__(self):
        self.mappings: Dict[int, MockMapping] = {}
        self._next_id = 1

    def assign(self, patient_id: int, doctor_id: int, notes: Optional[str] = None,
               patient: Optional[Any] = None, doctor: Optional[Any] = None) -> MockMapping:
        mapping = MockMapping(
            id=self._next_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            notes=notes,
            patient=patient,
            doctor=doctor
        )
        self.mappings[self._next_id] = mapping
        self._next_id += 1
        return mapping

    def get_by_id(self, mapping_id: int) -> Optional[MockMapping]:
        return self.mappings.get(mapping_id)

    def list_all(self) -> List[MockMapping]:
        return list(self.mappings.values())

    def list_by_user(self, user_id: int) -> List[MockMapping]:
        return [m for m in self.mappings.values() if m.patient and getattr(m.patient, 'created_by_id', None) == user_id]

    def get_by_patient(self, patient_id: int) -> List[MockMapping]:
        return [m for m in self.mappings.values() if m.patient_id == patient_id]

    def exists(self, patient_id: int, doctor_id: int) -> bool:
        return any(m.patient_id == patient_id and m.doctor_id == doctor_id for m in self.mappings.values())

    def delete(self, mapping_id: int) -> bool:
        if mapping_id in self.mappings:
            del self.mappings[mapping_id]
            return True
        return False
