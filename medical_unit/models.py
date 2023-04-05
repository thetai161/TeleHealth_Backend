import uuid
from django.db import models
from address.models import Address
from authentication.models import User

# Create your models here.


class MedicalUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    unsignedName = models.CharField(max_length=200)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='medicalUnit')
    detail_address = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="medicalUnit")

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medicalUnit"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.name)
