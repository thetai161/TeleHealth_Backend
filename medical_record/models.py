import uuid
from django.db import models
from authentication.models import User
from patient.models import Patient
from upload.models import File

# Create your models here.


class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='medicalRecord')
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='medicalRecord')
    patientInfo = models.CharField(max_length=255)
    result = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medicalRecord"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.patient)


class FileMedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicalRecord = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
