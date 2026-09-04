"""
URL configuration for Patient Management module.
"""
from django.urls import path
from apps.patients.views import PatientListCreateView, PatientDetailView

app_name = "patients"

urlpatterns = [
    path("", PatientListCreateView.as_view(), name="patient_list_create"),
    path("<int:pk>/", PatientDetailView.as_view(), name="patient_detail"),
]
