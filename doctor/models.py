import uuid
from django.db import models
from address.models import Address
from authentication.models import User
from medical_unit.models import MedicalUnit
from patient.models import Patient

# Create your models here.


class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    GENDER_CHOICE = (
        ("man", "Man"),
        ('woman', "Woman"),
    )
    gender = models.CharField(choices=GENDER_CHOICE, max_length=20)
    unsignedName = models.CharField(max_length=200)
    is_accept = models.BooleanField(default=False)
    medicalUnit = models.ForeignKey(
        MedicalUnit, on_delete=models.CASCADE, related_name='doctor', blank=True, null=True)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='doctor')
    detail_address = models.CharField(max_length=200)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor")

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.name)
