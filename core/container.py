"""
Central Dependency Injection Container.
Manages instantiation, configuration, and dependency wiring across the application.
"""
from typing import Dict, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.accounts.interfaces import IUserRepository, ITokenService
    from apps.accounts.services import AuthService
    from apps.doctors.interfaces import IDoctorRepository
    from apps.doctors.services import DoctorService
    from apps.patients.interfaces import IPatientRepository
    from apps.patients.services import PatientService
    from apps.mappings.interfaces import IMappingRepository
    from apps.mappings.services import MappingService


class Container:
    """
    Central Dependency Injection Container.
    Manages lazy factories and dependency resolution.
    """
    _factories: Dict[str, Callable[[], Any]] = {}

    @classmethod
    def register(cls, key: str, factory: Callable[[], Any]):
        """Register a custom factory for a dependency (used in tests/custom configurations)."""
        cls._factories[key] = factory

    @classmethod
    def get(cls, key: str) -> Any:
        """Resolve a dependency via its registered factory or default implementation."""
        if key in cls._factories:
            return cls._factories[key]()

        # Default production bindings
        if key == "user_repository":
            from apps.accounts.repositories import DjangoUserRepository
            return DjangoUserRepository()

        if key == "token_service":
            from apps.accounts.services import JWTTokenService
            return JWTTokenService()

        if key == "auth_service":
            from apps.accounts.services import AuthService
            return AuthService(
                user_repo=cls.user_repository(),
                token_service=cls.token_service()
            )

        if key == "doctor_repository":
            from apps.doctors.repositories import DjangoDoctorRepository
            return DjangoDoctorRepository()

        if key == "doctor_service":
            from apps.doctors.services import DoctorService
            return DoctorService(doctor_repo=cls.doctor_repository())

        if key == "patient_repository":
            from apps.patients.repositories import DjangoPatientRepository
            return DjangoPatientRepository()

        if key == "patient_service":
            from apps.patients.services import PatientService
            return PatientService(patient_repo=cls.patient_repository())

        if key == "mapping_repository":
            from apps.mappings.repositories import DjangoMappingRepository
            return DjangoMappingRepository()

        if key == "mapping_service":
            from apps.mappings.services import MappingService
            return MappingService(
                mapping_repo=cls.mapping_repository(),
                patient_repo=cls.patient_repository(),
                doctor_repo=cls.doctor_repository()
            )

        raise KeyError(f"Dependency '{key}' not registered in DI container.")

    # Convenience helper methods:
    @classmethod
    def user_repository(cls) -> "IUserRepository":
        return cls.get("user_repository")

    @classmethod
    def token_service(cls) -> "ITokenService":
        return cls.get("token_service")

    @classmethod
    def auth_service(cls) -> "AuthService":
        return cls.get("auth_service")

    @classmethod
    def doctor_repository(cls) -> "IDoctorRepository":
        return cls.get("doctor_repository")

    @classmethod
    def doctor_service(cls) -> "DoctorService":
        return cls.get("doctor_service")

    @classmethod
    def patient_repository(cls) -> "IPatientRepository":
        return cls.get("patient_repository")

    @classmethod
    def patient_service(cls) -> "PatientService":
        return cls.get("patient_service")

    @classmethod
    def mapping_repository(cls) -> "IMappingRepository":
        return cls.get("mapping_repository")

    @classmethod
    def mapping_service(cls) -> "MappingService":
        return cls.get("mapping_service")