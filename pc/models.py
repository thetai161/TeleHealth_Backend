import uuid
from django.db import models
from patient.models import Patient

# Create your models here.


class PcModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.BooleanField()
    file = models.FileField(blank=True, null=True, max_length=500)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='pc')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pc"
        ordering = ["created_at"]
