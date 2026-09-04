"""
Serializers for Accounts and Authentication module.
"""
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """Input serializer for user registration."""
    name = serializers.CharField(max_length=255, required=True, min_length=2)
    email = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(write_only=True, required=True, min_length=8)


class LoginSerializer(serializers.Serializer):
    """Input serializer for user login."""
    email = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.Serializer):
    """Output serializer for User model."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True, default=True)


class AuthDataSerializer(serializers.Serializer):
    """Inner data container for authentication responses."""
    user = UserSerializer()
    token = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for registration and login responses in OpenAPI documentation."""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = AuthDataSerializer()
