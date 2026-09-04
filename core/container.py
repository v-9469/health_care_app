"""
Central Dependency Injection Container (Phase 0: Core Infrastructure).
Provides factories and hooks for repositories and services as features are implemented.
"""
from typing import Dict, Any, Callable

class Container:
    """
    Central Dependency Injection Container.
    Features will register their repository and service factories here.
    """
    _factories: Dict[str, Callable[[], Any]] = {}

    @classmethod
    def register(cls, key: str, factory: Callable[[], Any]):
        """Register a factory for a dependency."""
        cls._factories[key] = factory

    @classmethod
    def get(cls, key: str) -> Any:
        """Resolve a dependency via its registered factory."""
        factory = cls._factories.get(key)
        if not factory:
            raise KeyError(f"Dependency '{key}' not registered in DI container.")
        return factory()

    # Convenience helper hooks for upcoming phases:
    @classmethod
    def user_repository(cls) -> Any:
        return cls.get("user_repository")

    @classmethod
    def patient_repository(cls) -> Any:
        return cls.get("patient_repository")

    @classmethod
    def doctor_repository(cls) -> Any:
        return cls.get("doctor_repository")

    @classmethod
    def mapping_repository(cls) -> Any:
        return cls.get("mapping_repository")
