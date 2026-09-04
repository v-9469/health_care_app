"""
API Views for Patient-Doctor Mapping with Dependency Injection.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.container import Container
from apps.mappings.serializers import (
    MappingCreateSerializer,
    MappingSerializer,
    MappingResponseSerializer,
    MappingListResponseSerializer
)


class MappingListCreateView(APIView):
    """
    List all patient-doctor mappings owned by the authenticated user or assign a doctor to a patient.
    GET /api/mappings/
    POST /api/mappings/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, mapping_service=None, **kwargs):
        super().__init__(**kwargs)
        self.mapping_service = mapping_service or Container.mapping_service()

    @extend_schema(
        operation_id="mappings_list",
        summary="List all patient-doctor mappings",
        description="Retrieves all doctor assignments for patients created by the authenticated user.",
        responses={200: OpenApiResponse(response=MappingListResponseSerializer, description="List of mappings")},
        tags=["Patient-Doctor Mappings"]
    )
    def get(self, request):
        mappings = self.mapping_service.list_mappings(user_id=request.user.id)
        serializer = MappingSerializer(mappings, many=True)
        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id="mappings_create",
        summary="Assign doctor to patient",
        description="Creates a new relationship mapping between a patient owned by the user and a doctor.",
        request=MappingCreateSerializer,
        responses={
            201: OpenApiResponse(response=MappingResponseSerializer, description="Doctor assigned successfully"),
            400: OpenApiResponse(description="Validation or duplicate mapping error"),
            404: OpenApiResponse(description="Patient or doctor not found"),
        },
        tags=["Patient-Doctor Mappings"]
    )
    def post(self, request):
        serializer = MappingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mapping = self.mapping_service.assign_doctor(
            user_id=request.user.id,
            patient_id=serializer.validated_data["patient_id"],
            doctor_id=serializer.validated_data["doctor_id"],
            notes=serializer.validated_data.get("notes")
        )

        return Response(
            {
                "success": True,
                "message": "Doctor successfully assigned to patient.",
                "data": MappingSerializer(mapping).data
            },
            status=status.HTTP_201_CREATED
        )


class PatientDoctorsDetailView(APIView):
    """
    Retrieve all doctors assigned to a specific patient, or delete a mapping.
    GET /api/mappings/<patient_id>/
    DELETE /api/mappings/<id>/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, mapping_service=None, **kwargs):
        super().__init__(**kwargs)
        self.mapping_service = mapping_service or Container.mapping_service()

    @extend_schema(
        operation_id="mappings_patient_doctors",
        summary="Get doctors assigned to a patient",
        description="Retrieves all assigned doctors for a specific patient owned by the authenticated user.",
        responses={
            200: OpenApiResponse(response=MappingListResponseSerializer, description="List of assigned doctors"),
            404: OpenApiResponse(description="Patient not found or unauthorized"),
        },
        tags=["Patient-Doctor Mappings"]
    )
    def get(self, request, pk):
        mappings = self.mapping_service.get_doctors_for_patient(
            user_id=request.user.id,
            patient_id=pk
        )
        serializer = MappingSerializer(mappings, many=True)
        return Response(
            {
                "success": True,
                "patient_id": pk,
                "count": len(serializer.data),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id="mappings_delete",
        summary="Unassign doctor from patient (Delete mapping)",
        description="Deletes a patient-doctor mapping record if the patient is owned by the user.",
        responses={
            204: OpenApiResponse(description="Doctor unassigned successfully"),
            404: OpenApiResponse(description="Mapping not found or unauthorized"),
        },
        tags=["Patient-Doctor Mappings"]
    )
    def delete(self, request, pk):
        self.mapping_service.delete_mapping(
            user_id=request.user.id,
            mapping_id=pk
        )
        return Response(
            {
                "success": True,
                "message": "Doctor unassigned from patient successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
