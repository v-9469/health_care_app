"""
Smoke Tests: Verifies Django settings, DI Container, and Pytest harness.
"""
from django.conf import settings
from core.container import Container


def test_django_settings_loaded():
    """Verify Django core settings are initialized properly."""
    assert settings.AUTH_USER_MODEL == 'accounts.User'
    assert 'rest_framework' in settings.INSTALLED_APPS
    assert 'rest_framework_simplejwt' in settings.INSTALLED_APPS
    assert 'drf_spectacular' in settings.INSTALLED_APPS
    assert 'apps.accounts' in settings.INSTALLED_APPS
    assert 'apps.doctors' in settings.INSTALLED_APPS
    assert settings.REST_FRAMEWORK['EXCEPTION_HANDLER'] == 'core.exceptions.custom_exception_handler'


def test_di_container_repositories_wiring(mock_container_dependencies):
    """Verify central Dependency Injection container resolves registered dependencies."""
    user_repo = Container.user_repository()
    token_service = Container.token_service()
    auth_service = Container.auth_service()
    doctor_repo = Container.doctor_repository()
    doctor_service = Container.doctor_service()

    assert user_repo is not None
    assert token_service is not None
    assert auth_service is not None
    assert doctor_repo is not None
    assert doctor_service is not None


def test_mock_repositories_in_memory():
    """Verify in-memory mock repositories support zero-database CRUD operations."""
    from tests.mocks import MockUserRepository, MockDoctorRepository

    user_repo = MockUserRepository()
    user = user_repo.create(name="Auth User", email="auth@healthcare.com", password="Password123!")
    assert user.id == 1
    assert user_repo.get_by_email("auth@healthcare.com") == user

    doctor_repo = MockDoctorRepository()
    doctor = doctor_repo.create(
        name="Dr. House",
        specialization="Diagnostics",
        contact_number="+1987654321",
        email="house@hospital.org"
    )
    assert doctor.id == 1
    assert len(doctor_repo.list_all()) == 1
    assert doctor_repo.get_by_email("house@hospital.org") == doctor
