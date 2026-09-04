"""
Phase 0 Smoke Tests: Verifies Django settings, DI Container, and Pytest harness.
"""
from django.conf import settings
from core.container import Container

def test_django_settings_loaded():
    """Verify Django core settings are initialized properly."""
    assert 'rest_framework' in settings.INSTALLED_APPS
    assert 'rest_framework_simplejwt' in settings.INSTALLED_APPS
    assert 'drf_spectacular' in settings.INSTALLED_APPS
    assert settings.REST_FRAMEWORK['EXCEPTION_HANDLER'] == 'core.exceptions.custom_exception_handler'

def test_di_container_repositories_wiring(mock_container_dependencies):
    """Verify central Dependency Injection container resolves registered repositories."""
    user_repo = Container.user_repository()
    patient_repo = Container.patient_repository()
    doctor_repo = Container.doctor_repository()
    mapping_repo = Container.mapping_repository()

    assert user_repo is not None
    assert patient_repo is not None
    assert doctor_repo is not None
    assert mapping_repo is not None

def test_mock_repositories_in_memory():
    """Verify in-memory mock repositories support zero-database CRUD operations."""
    from tests.mocks import MockUserRepository, MockPatientRepository, MockDoctorRepository, MockMappingRepository

    user_repo = MockUserRepository()
    user = user_repo.create(name="Init User", email="init@healthcare.com", password="Password123!")
    assert user.id == 1
    assert user_repo.get_by_email("init@healthcare.com") == user

    patient_repo = MockPatientRepository()
    patient = patient_repo.create(user_id=user.id, name="Init Patient", age=30, gender="M", contact_number="+123456789")
    assert patient.id == 1
    assert len(patient_repo.list_by_user(user.id)) == 1

    doctor_repo = MockDoctorRepository()
    doctor = doctor_repo.create(name="Dr. House", specialization="Diagnostics", contact_number="+1987654321", email="house@hospital.org")
    assert doctor.id == 1
    assert len(doctor_repo.list_all()) == 1

    mapping_repo = MockMappingRepository()
    mapping = mapping_repo.assign(patient_id=patient.id, doctor_id=doctor.id, notes="Primary")
    assert mapping.id == 1
    assert mapping_repo.exists(patient.id, doctor.id) is True
