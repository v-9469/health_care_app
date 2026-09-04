"""
Central Dependency Injection Container.
Manages instantiation, configuration, and dependency wiring across the application.
"""
from typing import Dict, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.doctors.interfaces import IDoctorRepository
    from apps.doctors.services import DoctorService


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
        if key == "doctor_repository":
            from apps.doctors.repositories import DjangoDoctorRepository
            return DjangoDoctorRepository()

        if key == "doctor_service":
            from apps.doctors.services import DoctorService
            return DoctorService(doctor_repo=cls.doctor_repository())

        raise KeyError(f"Dependency '{key}' not registered in DI container.")

    # Convenience helper methods:
    @classmethod
    def doctor_repository(cls) -> "IDoctorRepository":
        return cls.get("doctor_repository")

    @classmethod
    def doctor_service(cls) -> "DoctorService":
        return cls.get("doctor_service")