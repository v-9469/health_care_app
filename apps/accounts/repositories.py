"""
Django ORM implementation of IUserRepository.
"""
from typing import Optional
from django.contrib.auth import get_user_model
from apps.accounts.interfaces import IUserRepository

User = get_user_model()


class DjangoUserRepository(IUserRepository):
    """Concrete repository interacting with PostgreSQL via Django ORM."""

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email__iexact=email.strip())
        except User.DoesNotExist:
            return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def create(self, name: str, email: str, password: str, **kwargs) -> User:
        return User.objects.create_user(
            email=email.strip().lower(),
            name=name.strip(),
            password=password,
            **kwargs
        )
