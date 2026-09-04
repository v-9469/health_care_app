"""
Pytest global fixtures and Dependency Injection setup for Auth and Doctor Management.
"""
import pytest
from rest_framework.test import APIClient
from core.container import Container
from tests.mocks import (
    MockUserRepository,
    MockDoctorRepository,
    MockUser
)
from apps.accounts.services import AuthService, JWTTokenService
from apps.doctors.services import DoctorService


@pytest.fixture(autouse=True)
def mock_container_dependencies():
    """
    Overrides the DI Container with in-memory mock repositories for all tests.
    """
    mock_user_repo = MockUserRepository()
    token_service = JWTTokenService()
    auth_service = AuthService(user_repo=mock_user_repo, token_service=token_service)

    mock_doctor_repo = MockDoctorRepository()
    doctor_service = DoctorService(doctor_repo=mock_doctor_repo)

    Container.register("user_repository", lambda: mock_user_repo)
    Container.register("token_service", lambda: token_service)
    Container.register("auth_service", lambda: auth_service)
    Container.register("doctor_repository", lambda: mock_doctor_repo)
    Container.register("doctor_service", lambda: doctor_service)

    return {
        "user_repo": mock_user_repo,
        "token_service": token_service,
        "auth_service": auth_service,
        "doctor_repo": mock_doctor_repo,
        "doctor_service": doctor_service,
    }


@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient fixture."""
    return APIClient()


@pytest.fixture
def auth_user(mock_container_dependencies):
    """Mock authenticated user instance stored in the mock repository."""
    user_repo = mock_container_dependencies["user_repo"]
    return user_repo.create(
        name="Dr. Administrator",
        email="admin@hospital.org",
        password="ValidPassword123!",
        is_active=True,
        is_staff=True
    )


@pytest.fixture
def auth_client(api_client, auth_user, mock_container_dependencies):
    """Authenticated DRF APIClient fixture pre-loaded with valid JWT token."""
    token_service = mock_container_dependencies["token_service"]
    token = token_service.generate_token_for_user(auth_user)

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.force_authenticate(user=auth_user)
    api_client.test_user = auth_user
    return api_client
