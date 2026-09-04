"""
Pytest Feature Tests: Authentication & User Security (In-Memory Mock DB).
"""
import pytest
from rest_framework import status


class TestUserRegistration:
    """Tests for POST /api/auth/register/"""

    def test_registration_success(self, api_client, mock_container_dependencies):
        payload = {
            "name": "Dr. John Watson",
            "email": "watson@bakerstreet.com",
            "password": "SuperSecretPassword123!"
        }
        response = api_client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "user" in response.data["data"]
        assert response.data["data"]["user"]["email"] == "watson@bakerstreet.com"
        assert response.data["data"]["user"]["name"] == "Dr. John Watson"
        assert "token" in response.data["data"]
        assert isinstance(response.data["data"]["token"], str)
        assert len(response.data["data"]["token"]) > 20

        # Verify mock repository stored the user
        user_repo = mock_container_dependencies["user_repo"]
        saved_user = user_repo.get_by_email("watson@bakerstreet.com")
        assert saved_user is not None
        assert saved_user.name == "Dr. John Watson"

    def test_registration_duplicate_email_fails(self, api_client, auth_user):
        payload = {
            "name": "Imposter User",
            "email": auth_user.email,  # same email as existing user
            "password": "Password12345!"
        }
        response = api_client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "DUPLICATE_RESOURCE"

    def test_registration_short_password_fails(self, api_client):
        payload = {
            "name": "Alice Smith",
            "email": "alice@test.com",
            "password": "123"  # too short (< 8 chars)
        }
        response = api_client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_registration_invalid_email_fails(self, api_client):
        payload = {
            "name": "Alice Smith",
            "email": "not-a-valid-email",
            "password": "Password123!"
        }
        response = api_client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_registration_missing_name_fails(self, api_client):
        payload = {
            "email": "noname@test.com",
            "password": "Password123!"
        }
        response = api_client.post("/api/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


class TestUserLogin:
    """Tests for POST /api/auth/login/"""

    def test_login_success(self, api_client, auth_user):
        payload = {
            "email": auth_user.email,
            "password": "ValidPassword123!"
        }
        response = api_client.post("/api/auth/login/", payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "token" in response.data["data"]
        assert isinstance(response.data["data"]["token"], str)
        assert response.data["data"]["user"]["email"] == auth_user.email
        assert response.data["data"]["user"]["name"] == auth_user.name

    def test_login_invalid_password_fails(self, api_client, auth_user):
        payload = {
            "email": auth_user.email,
            "password": "WrongPassword123!"
        }
        response = api_client.post("/api/auth/login/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "UNAUTHORIZED"

    def test_login_nonexistent_email_fails(self, api_client):
        payload = {
            "email": "nonexistent@unknown.com",
            "password": "AnyPassword123!"
        }
        response = api_client.post("/api/auth/login/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_login_missing_fields_fails(self, api_client):
        payload = {
            "email": "onlyemail@test.com"
        }
        response = api_client.post("/api/auth/login/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


class TestUserProfileAndProtectedEndpoints:
    """Tests for GET /api/auth/me/"""

    def test_get_profile_authenticated(self, auth_client, auth_user):
        response = auth_client.get("/api/auth/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["email"] == auth_user.email
        assert response.data["data"]["name"] == auth_user.name

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get("/api/auth/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
