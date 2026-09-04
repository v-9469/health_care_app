"""
Doctor model with database indexing for high-speed queries.
"""
from django.db import models


class Doctor(models.Model):
    """
    Doctor domain model storing professional and contact information.
    """
    name = models.CharField(max_length=255, verbose_name="Doctor Full Name")
    specialization = models.CharField(max_length=255, verbose_name="Medical Specialization")
    contact_number = models.CharField(max_length=20, verbose_name="Contact Phone Number")
    email = models.EmailField(unique=True, max_length=255, verbose_name="Professional Email Address")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Years of Experience")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"], name="idx_doctor_email"),
            models.Index(fields=["specialization"], name="idx_doctor_specialization"),
            models.Index(fields=["name"], name="idx_doctor_name"),
            models.Index(fields=["-created_at"], name="idx_doctor_created_at"),
        ]

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
