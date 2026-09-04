"""
API Views for Patient Management with Dependency Injection.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from core.container import Container
from apps.patients.serializers import (
    PatientSerializer,
    PatientUpdateSerializer,
    PatientResponseSerializer
)


class PatientListCreateView(APIView):
    """
    List all patients created by the authenticated user or add a new patient.
    GET /api/patients/
    POST /api/patients/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, patient_service=None, **kwargs):
        super().__init__(**kwargs)
        self.patient_service = patient_service or Container.patient_service()

    @extend_schema(
        operation_id="patients_list",
        summary="List user's patients",
        description="Retrieves all patients created by the authenticated user. Supports keyword search.",
        parameters=[
            OpenApiParameter("search", str, description="Search by name, contact number, or email", required=False),
        ],
        responses={200: OpenApiResponse(response=PatientSerializer(many=True), description="List of user's patients")},
        tags=["Patient Management"]
    )
    def get(self, request):
        search = request.query_params.get("search")
        patients = self.patient_service.list_patients(
            user_id=request.user.id,
            search=search
        )
        serializer = PatientSerializer(patients, many=True)
        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id="patients_create",
        summary="Add a new patient",
        description="Creates a new patient record scoped to the authenticated user.",
        request=PatientSerializer,
        responses={
            201: OpenApiResponse(response=PatientResponseSerializer, description="Patient created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Patient Management"]
    )
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = self.patient_service.create_patient(
            user_id=request.user.id,
            data=serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "Patient record created successfully.",
                "data": PatientSerializer(patient).data
            },
            status=status.HTTP_201_CREATED
        )


class PatientDetailView(APIView):
    """
    Retrieve, update, or delete a specific patient.
    GET /api/patients/<id>/
    PUT /api/patients/<id>/
    PATCH /api/patients/<id>/
    DELETE /api/patients/<id>/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, patient_service=None, **kwargs):
        super().__init__(**kwargs)
        self.patient_service = patient_service or Container.patient_service()

    @extend_schema(
        operation_id="patients_retrieve",
        summary="Get patient details",
        description="Retrieves details of a specific patient owned by the authenticated user.",
        responses={
            200: OpenApiResponse(response=PatientResponseSerializer, description="Patient details"),
            404: OpenApiResponse(description="Patient not found or unauthorized"),
        },
        tags=["Patient Management"]
    )
    def get(self, request, pk):
        patient = self.patient_service.get_patient(patient_id=pk, user_id=request.user.id)
        return Response(
            {
                "success": True,
                "data": PatientSerializer(patient).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Update patient details (Full)",
        description="Updates all fields of an owned patient record.",
        request=PatientSerializer,
        responses={
            200: OpenApiResponse(response=PatientResponseSerializer, description="Patient updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Patient not found or unauthorized"),
        },
        tags=["Patient Management"]
    )
    def put(self, request, pk):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = self.patient_service.update_patient(
            patient_id=pk,
            user_id=request.user.id,
            update_data=serializer.validated_data
        )
        return Response(
            {
                "success": True,
                "message": "Patient record updated successfully.",
                "data": PatientSerializer(patient).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Update patient details (Partial)",
        description="Partially updates fields of an owned patient record.",
        request=PatientUpdateSerializer,
        responses={
            200: OpenApiResponse(response=PatientResponseSerializer, description="Patient updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Patient not found or unauthorized"),
        },
        tags=["Patient Management"]
    )
    def patch(self, request, pk):
        serializer = PatientUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = self.patient_service.update_patient(
            patient_id=pk,
            user_id=request.user.id,
            update_data=serializer.validated_data
        )
        return Response(
            {
                "success": True,
                "message": "Patient record updated successfully.",
                "data": PatientSerializer(patient).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Delete a patient",
        description="Deletes a patient record owned by the authenticated user.",
        responses={
            204: OpenApiResponse(description="Patient record deleted"),
            404: OpenApiResponse(description="Patient not found or unauthorized"),
        },
        tags=["Patient Management"]
    )
    def delete(self, request, pk):
        self.patient_service.delete_patient(patient_id=pk, user_id=request.user.id)
        return Response(
            {
                "success": True,
                "message": "Patient record deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
