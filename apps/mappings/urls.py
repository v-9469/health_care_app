"""
URL configuration for Patient-Doctor Mapping module.
"""
from django.urls import path
from apps.mappings.views import (
    MappingListCreateView,
    PatientDoctorsDetailView
)

app_name = "mappings"

urlpatterns = [
    path("", MappingListCreateView.as_view(), name="mapping_list_create"),
    path("<int:pk>/", PatientDoctorsDetailView.as_view(), name="mapping_patient_or_detail"),
]
