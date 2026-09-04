"""
Authentication and User Domain Services with Dependency Injection.
"""
from typing import Dict, Any
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.interfaces import IUserRepository, ITokenService
from core.exceptions import (
    DuplicateResourceException,
    UnauthorizedException,
    NotFoundException,
    ValidationException
)


class JWTTokenService(ITokenService):
    """Generates standard JWT authentication token."""

    def generate_token_for_user(self, user: Any) -> str:
        if hasattr(user, 'id'):
            refresh = RefreshToken()
            refresh['user_id'] = user.id
            refresh['email'] = getattr(user, 'email', '')
            refresh['name'] = getattr(user, 'name', '')

            return str(refresh.access_token)
        raise ValidationException("Invalid user object provided for token generation.")


class AuthService:
    """Domain service managing user authentication and account lifecycle."""

    def __init__(self, user_repo: IUserRepository, token_service: ITokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def register(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Registers a new user and issues a JWT authentication token."""
        clean_email = email.strip().lower() if email else ""
        clean_name = name.strip() if name else ""

        if not clean_email or '@' not in clean_email:
            raise ValidationException("A valid email address is required.")

        if not clean_name or len(clean_name) < 2:
            raise ValidationException("Name must be at least 2 characters long.")

        if not password or len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long.")

        existing_user = self.user_repo.get_by_email(clean_email)
        if existing_user:
            raise DuplicateResourceException("A user with this email address already exists.")

        user = self.user_repo.create(
            name=clean_name,
            email=clean_email,
            password=password
        )

        token = self.token_service.generate_token_for_user(user)
        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'token': token
        }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticates user credentials and returns a JWT token."""
        clean_email = email.strip().lower() if email else ""
        if not clean_email or not password:
            raise ValidationException("Email and password are required.")

        user = self.user_repo.get_by_email(clean_email)
        if not user:
            raise UnauthorizedException("Invalid email or password.")

        if hasattr(user, 'check_password'):
            if not user.check_password(password):
                raise UnauthorizedException("Invalid email or password.")
        else:
            if getattr(user, 'password', '') != password:
                raise UnauthorizedException("Invalid email or password.")

        if not getattr(user, 'is_active', True):
            raise UnauthorizedException("User account is disabled.")

        token = self.token_service.generate_token_for_user(user)
        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'token': token
        }

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Retrieves profile of the specified user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_active': getattr(user, 'is_active', True),
        }
