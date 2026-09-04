"""
DRF Serializers for Doctor module.
"""
from rest_framework import serializers


class DoctorSerializer(serializers.Serializer):
    """Serializer representing Doctor entities."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True, min_length=2)
    specialization = serializers.CharField(max_length=255, required=True)
    contact_number = serializers.CharField(max_length=20, required=True, min_length=5)
    email = serializers.EmailField(max_length=255, required=True)
    experience_years = serializers.IntegerField(required=False, default=0, min_value=0)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class DoctorUpdateSerializer(serializers.Serializer):
    """Serializer for partial/full updates of Doctor records."""
    name = serializers.CharField(max_length=255, required=False, min_length=2)
    specialization = serializers.CharField(max_length=255, required=False)
    contact_number = serializers.CharField(max_length=20, required=False, min_length=5)
    email = serializers.EmailField(max_length=255, required=False)
    experience_years = serializers.IntegerField(required=False, min_value=0)


class DoctorResponseSerializer(serializers.Serializer):
    """Standardized API response serializer for Swagger documentation."""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False)
    data = DoctorSerializer(allow_null=True)
