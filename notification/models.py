import uuid
from django.db import models
from authentication.models import User


class Notification(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification", null=True)
    content = models.CharField(max_length=100, null=True, blank=True)
    linkId = models.CharField(max_length=50, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]
