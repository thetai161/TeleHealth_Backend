from django.db import models
import uuid


def upload_to(instance, filename):
    return '/'.join([str(instance.folder), str(instance.name), filename])


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    folder = models.CharField(max_length=50, null=True)
    file = models.FileField(upload_to=upload_to,
                            blank=True, null=True, max_length=500)

    class Meta:
        db_table = "file"
