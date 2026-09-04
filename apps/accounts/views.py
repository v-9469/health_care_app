"""
API Views for Authentication and Account Management with Dependency Injection.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.container import Container
from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthResponseSerializer
)


class RegisterView(APIView):
    """
    Register a new user account.
    POST /api/auth/register/
    """
    permission_classes = [AllowAny]

    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or Container.auth_service()

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with name, email, and password, returning user info and JWT tokens.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(response=AuthResponseSerializer, description="User successfully registered"),
            400: OpenApiResponse(description="Validation error or duplicate email"),
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = self.auth_service.register(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "data": result
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    Log in a user and return JWT access and refresh tokens.
    POST /api/auth/login/
    """
    permission_classes = [AllowAny]

    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or Container.auth_service()

    @extend_schema(
        summary="Log in user",
        description="Authenticates user credentials and returns JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(response=AuthResponseSerializer, description="Login successful"),
            400: OpenApiResponse(description="Missing required fields"),
            401: OpenApiResponse(description="Invalid email or password"),
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = self.auth_service.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": result
            },
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    """
    Retrieve current authenticated user's profile.
    GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, auth_service=None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or Container.auth_service()

    @extend_schema(
        summary="Get current user profile",
        description="Retrieves profile information of the currently authenticated user.",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Profile retrieved successfully"),
            401: OpenApiResponse(description="Unauthenticated request"),
        },
        tags=["Authentication"]
    )
    def get(self, request):
        user_id = request.user.id
        profile = self.auth_service.get_user_profile(user_id)
        return Response(
            {
                "success": True,
                "data": profile
            },
            status=status.HTTP_200_OK
        )
