import uuid
from django.db import models
from address.models import Address
from authentication.models import User
from patient.models import Patient
from doctor.models import Doctor

# Create your models here.


class PatientManagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='patientmanagement')
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='patientmanagement')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patientmanagement"
        ordering = ["created_at"]
