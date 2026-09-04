"""
DRF Serializers for Patient-Doctor Mapping module.
"""
from rest_framework import serializers


class MappingPatientSummarySerializer(serializers.Serializer):
    """Compact summary serializer for patient in mapping responses."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    gender = serializers.CharField(read_only=True)
    contact_number = serializers.CharField(read_only=True)


class MappingDoctorSummarySerializer(serializers.Serializer):
    """Compact summary serializer for doctor in mapping responses."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    specialization = serializers.CharField(read_only=True)
    contact_number = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    experience_years = serializers.IntegerField(read_only=True)


class MappingCreateSerializer(serializers.Serializer):
    """Serializer for assigning a doctor to a patient."""
    patient_id = serializers.IntegerField(required=True, min_value=1, help_text="ID of the patient")
    doctor_id = serializers.IntegerField(required=True, min_value=1, help_text="ID of the doctor")
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Optional clinical assignment notes"
    )


class MappingSerializer(serializers.Serializer):
    """Full representation serializer for Patient-Doctor Mapping."""
    id = serializers.IntegerField(read_only=True)
    patient_id = serializers.IntegerField(read_only=True)
    doctor_id = serializers.IntegerField(read_only=True)
    patient = MappingPatientSummarySerializer(read_only=True, allow_null=True)
    doctor = MappingDoctorSummarySerializer(read_only=True, allow_null=True)
    assigned_date = serializers.DateTimeField(read_only=True)
    notes = serializers.CharField(read_only=True, allow_null=True)


class MappingResponseSerializer(serializers.Serializer):
    """Standardized single-item API response serializer for Swagger documentation."""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False)
    data = MappingSerializer(allow_null=True)


class MappingListResponseSerializer(serializers.Serializer):
    """Standardized list API response serializer for Swagger documentation."""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField(default=0)
    data = MappingSerializer(many=True)
