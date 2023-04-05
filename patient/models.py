import uuid
from django.db import models
from address.models import Address
from authentication.models import User
from medical_unit.models import MedicalUnit
# Create your models here.


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    GENDER_CHOICE = (
        ("man", "Man"),
        ('woman', "Woman"),
    )
    gender = models.CharField(choices=GENDER_CHOICE, max_length=20)
    unsignedName = models.CharField(max_length=200, blank=True)
    medicalUnit = models.ForeignKey(
        MedicalUnit, on_delete=models.CASCADE, related_name='patient')
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='patient')
    detail_address = models.CharField(max_length=200, blank=True)
    ethnic = models.CharField(max_length=200)
    dateOfBirth = models.DateField()
    insuranceCode = models.CharField(max_length=20, blank=True)
    identification = models.CharField(max_length=20, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient")

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patient"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.name)
