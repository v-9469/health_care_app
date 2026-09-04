"""
DRF Serializers for Patient module.
"""
from rest_framework import serializers


class PatientSerializer(serializers.Serializer):
    """Serializer representing Patient entities."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True, min_length=2)
    age = serializers.IntegerField(required=True, min_value=0, max_value=150)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required=True)
    contact_number = serializers.CharField(max_length=20, required=True, min_length=5)
    email = serializers.EmailField(max_length=255, required=False, allow_null=True, allow_blank=True)
    address = serializers.CharField(required=True)
    medical_history = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    created_by_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PatientUpdateSerializer(serializers.Serializer):
    """Serializer for partial/full updates of Patient records."""
    name = serializers.CharField(max_length=255, required=False, min_length=2)
    age = serializers.IntegerField(required=False, min_value=0, max_value=150)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required=False)
    contact_number = serializers.CharField(max_length=20, required=False, min_length=5)
    email = serializers.EmailField(max_length=255, required=False, allow_null=True, allow_blank=True)
    address = serializers.CharField(required=False)
    medical_history = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class PatientResponseSerializer(serializers.Serializer):
    """Standardized API response serializer for Swagger documentation."""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False)
    data = PatientSerializer(allow_null=True)
