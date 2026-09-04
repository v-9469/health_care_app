"""
API Views for Doctor Management with Dependency Injection.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from core.container import Container
from apps.doctors.serializers import (
    DoctorSerializer,
    DoctorUpdateSerializer,
    DoctorResponseSerializer
)


class DoctorListCreateView(APIView):
    """
    List all doctors or create a new doctor profile.
    GET /api/doctors/
    POST /api/doctors/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, doctor_service=None, **kwargs):
        super().__init__(**kwargs)
        self.doctor_service = doctor_service or Container.doctor_service()

    @extend_schema(
        summary="List all doctors",
        description="Retrieves a list of all doctors. Supports filtering by specialization and text search.",
        parameters=[
            OpenApiParameter("specialization", str, description="Filter by medical specialty (e.g. Cardiology)", required=False),
            OpenApiParameter("search", str, description="Search by name, specialization, or email", required=False),
        ],
        responses={200: OpenApiResponse(response=DoctorSerializer(many=True), description="List of doctors")},
        tags=["Doctor Management"]
    )
    def get(self, request):
        specialization = request.query_params.get("specialization")
        search = request.query_params.get("search")

        doctors = self.doctor_service.list_doctors(
            specialization=specialization,
            search=search
        )
        serializer = DoctorSerializer(doctors, many=True)
        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Create a new doctor",
        description="Adds a new doctor to the system. Email must be unique.",
        request=DoctorSerializer,
        responses={
            201: OpenApiResponse(response=DoctorResponseSerializer, description="Doctor created successfully"),
            400: OpenApiResponse(description="Validation error or duplicate email"),
        },
        tags=["Doctor Management"]
    )
    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = self.doctor_service.create_doctor(
            name=serializer.validated_data["name"],
            specialization=serializer.validated_data["specialization"],
            contact_number=serializer.validated_data["contact_number"],
            email=serializer.validated_data["email"],
            experience_years=serializer.validated_data.get("experience_years", 0)
        )

        return Response(
            {
                "success": True,
                "message": "Doctor record created successfully.",
                "data": DoctorSerializer(doctor).data
            },
            status=status.HTTP_201_CREATED
        )


class DoctorDetailView(APIView):
    """
    Retrieve, update, or delete a specific doctor.
    GET /api/doctors/<id>/
    PUT /api/doctors/<id>/
    PATCH /api/doctors/<id>/
    DELETE /api/doctors/<id>/
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, doctor_service=None, **kwargs):
        super().__init__(**kwargs)
        self.doctor_service = doctor_service or Container.doctor_service()

    @extend_schema(
        summary="Get doctor details",
        description="Retrieves full details of a specific doctor by ID.",
        responses={
            200: OpenApiResponse(response=DoctorResponseSerializer, description="Doctor details"),
            404: OpenApiResponse(description="Doctor not found"),
        },
        tags=["Doctor Management"]
    )
    def get(self, request, pk):
        doctor = self.doctor_service.get_doctor(pk)
        return Response(
            {
                "success": True,
                "data": DoctorSerializer(doctor).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Update doctor details (Full)",
        description="Updates all fields of a doctor record.",
        request=DoctorSerializer,
        responses={
            200: OpenApiResponse(response=DoctorResponseSerializer, description="Doctor updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Doctor not found"),
        },
        tags=["Doctor Management"]
    )
    def put(self, request, pk):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = self.doctor_service.update_doctor(pk, serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Doctor record updated successfully.",
                "data": DoctorSerializer(doctor).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Update doctor details (Partial)",
        description="Partially updates fields of a doctor record.",
        request=DoctorUpdateSerializer,
        responses={
            200: OpenApiResponse(response=DoctorResponseSerializer, description="Doctor updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Doctor not found"),
        },
        tags=["Doctor Management"]
    )
    def patch(self, request, pk):
        serializer = DoctorUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = self.doctor_service.update_doctor(pk, serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Doctor record updated successfully.",
                "data": DoctorSerializer(doctor).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Delete a doctor",
        description="Deletes a doctor record from the system.",
        responses={
            204: OpenApiResponse(description="Doctor record deleted"),
            404: OpenApiResponse(description="Doctor not found"),
        },
        tags=["Doctor Management"]
    )
    def delete(self, request, pk):
        self.doctor_service.delete_doctor(pk)
        return Response(
            {
                "success": True,
                "message": "Doctor record deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
