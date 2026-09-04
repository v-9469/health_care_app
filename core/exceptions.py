"""
Custom exception classes and standardized DRF exception handler.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed
)

# Domain Specific Exceptions
class HealthcareException(Exception):
    """Base exception for domain layer."""
    default_message = "An error occurred."
    default_code = "APP_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(HealthcareException):
    default_message = "Requested resource was not found."
    default_code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedException(HealthcareException):
    default_message = "Unauthorized access."
    default_code = "UNAUTHORIZED"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(HealthcareException):
    default_message = "You do not have permission to perform this action."
    default_code = "FORBIDDEN"
    status_code = status.HTTP_403_FORBIDDEN


class ValidationException(HealthcareException):
    default_message = "Invalid input data."
    default_code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST


class DuplicateResourceException(HealthcareException):
    default_message = "A resource with these details already exists."
    default_code = "DUPLICATE_RESOURCE"
    status_code = status.HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):
    """
    Standardized exception handler for DRF views.
    Ensures all error responses return uniform structure:
    {
        "success": false,
        "error": {
            "code": "...",
            "message": "...",
            "details": {...}
        }
    }
    """
    # Handle domain-specific exceptions
    if isinstance(exc, HealthcareException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            },
            status=exc.status_code
        )

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "API_ERROR"
        message = "An error occurred."
        details = {}

        if isinstance(exc, DRFValidationError):
            error_code = "VALIDATION_ERROR"
            message = "Validation failed for one or more fields."
            details = response.data
        elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            error_code = "AUTHENTICATION_FAILED"
            message = str(exc.detail) if hasattr(exc, 'detail') else "Authentication credentials were not provided or are invalid."
        elif isinstance(exc, PermissionDenied):
            error_code = "PERMISSION_DENIED"
            message = str(exc.detail) if hasattr(exc, 'detail') else "You do not have permission to perform this action."
        elif isinstance(exc, NotFound):
            error_code = "NOT_FOUND"
            message = str(exc.detail) if hasattr(exc, 'detail') else "Resource not found."
        elif isinstance(exc, MethodNotAllowed):
            error_code = "METHOD_NOT_ALLOWED"
            message = str(exc.detail) if hasattr(exc, 'detail') else "Method not allowed."
        else:
            if isinstance(response.data, dict) and 'detail' in response.data:
                message = str(response.data['detail'])
            else:
                details = response.data

        response.data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details
            }
        }
        return response

    # Unhandled server errors (500)
    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": str(exc)
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
