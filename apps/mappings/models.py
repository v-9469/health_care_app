"""
Patient-Doctor Mapping domain model with relational integrity and database indexing.
"""
from django.db import models


class PatientDoctorMapping(models.Model):
    """
    Associative domain model linking a Patient to an assigned Doctor.
    Enforces uniqueness so a patient cannot be mapped to the same doctor multiple times.
    """
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        verbose_name="Assigned Patient"
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        verbose_name="Assigned Doctor"
    )
    assigned_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Assignment Date"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Clinical Assignment Notes"
    )

    class Meta:
        verbose_name = "Patient-Doctor Mapping"
        verbose_name_plural = "Patient-Doctor Mappings"
        ordering = ["-assigned_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="unique_patient_doctor_mapping"
            )
        ]
        indexes = [
            models.Index(fields=["patient", "doctor"], name="idx_map_patient_doctor"),
            models.Index(fields=["doctor"], name="idx_map_doctor"),
            models.Index(fields=["-assigned_date"], name="idx_map_assigned_date"),
        ]

    def __str__(self):
        return f"Mapping: Patient #{self.patient_id} -> Doctor #{self.doctor_id} ({self.assigned_date.strftime('%Y-%m-%d')})"
