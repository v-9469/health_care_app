"""
URL configuration for Doctor Management module.
"""
from django.urls import path
from apps.doctors.views import DoctorListCreateView, DoctorDetailView

app_name = "doctors"

urlpatterns = [
    path("", DoctorListCreateView.as_view(), name="doctor_list_create"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
]
