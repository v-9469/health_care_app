"""
Pytest global fixtures and Dependency Injection setup for Phase 0.
"""
import pytest
from rest_framework.test import APIClient
from core.container import Container
from tests.mocks import (
    MockUserRepository,
    MockPatientRepository,
    MockDoctorRepository,
    MockMappingRepository
)

@pytest.fixture(autouse=True)
def mock_container_dependencies():
    """
    Overrides the DI Container with in-memory mock repositories for Phase 0.
    """
    mock_user_repo = MockUserRepository()
    mock_patient_repo = MockPatientRepository()
    mock_doctor_repo = MockDoctorRepository()
    mock_mapping_repo = MockMappingRepository()

    Container.register("user_repository", lambda: mock_user_repo)
    Container.register("patient_repository", lambda: mock_patient_repo)
    Container.register("doctor_repository", lambda: mock_doctor_repo)
    Container.register("mapping_repository", lambda: mock_mapping_repo)

    return {
        "user_repo": mock_user_repo,
        "patient_repo": mock_patient_repo,
        "doctor_repo": mock_doctor_repo,
        "mapping_repo": mock_mapping_repo,
    }

@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient fixture."""
    return APIClient()
