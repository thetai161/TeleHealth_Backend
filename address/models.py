from statistics import mode
import uuid
from django.db import models
from authentication.models import User

# Create your models here.


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=200)
    province = models.CharField(max_length=200)
    district = models.CharField(max_length=200)
    ward = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "address"
        ordering = ["created_at"]
