"""
Patient domain model with composite database indexing.
"""
from django.db import models
from django.conf import settings


class Patient(models.Model):
    """
    Patient domain model storing personal, contact, and medical records.
    Scoped to the authenticated user who created the record.
    """
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255, verbose_name="Patient Full Name")
    age = models.PositiveIntegerField(verbose_name="Patient Age")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Gender")
    contact_number = models.CharField(max_length=20, verbose_name="Contact Phone Number")
    email = models.EmailField(blank=True, null=True, max_length=255, verbose_name="Contact Email Address")
    address = models.TextField(verbose_name="Residential Address")
    medical_history = models.TextField(blank=True, null=True, verbose_name="Medical Notes & History")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        verbose_name="Created By User"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "-created_at"], name="idx_patient_user_created"),
            models.Index(fields=["name"], name="idx_patient_name"),
            models.Index(fields=["contact_number"], name="idx_patient_contact"),
        ]

    def __str__(self):
        return f"{self.name} (Age: {self.age}, {self.gender})"
