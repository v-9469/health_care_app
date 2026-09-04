"""
Repository and Service Interfaces for Accounts and Authentication.
"""
from typing import Protocol, Optional, Any


class IUserRepository(Protocol):
    """Contract for User data access."""

    def get_by_email(self, email: str) -> Optional[Any]: ...
    def get_by_id(self, user_id: int) -> Optional[Any]: ...
    def create(self, name: str, email: str, password: str, **kwargs) -> Any: ...


class ITokenService(Protocol):
    """Contract for JWT token generation."""

    def generate_token_for_user(self, user: Any) -> str: ...
