"""
Pytest global fixtures and Dependency Injection setup for Doctor Management.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import AnonymousUser
from core.container import Container
from tests.mocks import (
    MockDoctorRepository,
    MockUser
)
from apps.doctors.services import DoctorService


@pytest.fixture(autouse=True)
def mock_container_dependencies():
    """
    Overrides the DI Container with in-memory mock repositories for all tests.
    """
    mock_doctor_repo = MockDoctorRepository()
    doctor_service = DoctorService(doctor_repo=mock_doctor_repo)

    Container.register("doctor_repository", lambda: mock_doctor_repo)
    Container.register("doctor_service", lambda: doctor_service)

    return {
        "doctor_repo": mock_doctor_repo,
        "doctor_service": doctor_service,
    }


@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient fixture."""
    return APIClient()


@pytest.fixture
def auth_user():
    """Mock authenticated user instance."""
    return MockUser(
        id=1,
        name="Dr. Administrator",
        email="admin@hospital.org",
        password="ValidPassword123!",
        is_active=True,
        is_staff=True
    )


@pytest.fixture
def auth_client(api_client, auth_user):
    """Authenticated DRF APIClient fixture."""
    api_client.force_authenticate(user=auth_user)
    api_client.test_user = auth_user
    return api_client
