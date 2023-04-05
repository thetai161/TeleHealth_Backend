
from profile import Profile
from django.db import models
from authentication.models import User
from patient.models import Patient


class UserUploadedFile(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    id_file = models.CharField(max_length=9, null=True)
    drive_id = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)


class ResultFile(models.Model):
    upload_file = models.ForeignKey(
        UserUploadedFile, on_delete=models.CASCADE, null=False)
    right_lung = models.CharField(max_length=20)
    left_lung = models.CharField(max_length=20)
    lung_volume = models.CharField(max_length=20)
    url = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.upload_file)


class FileTLC(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    f_name = models.CharField(max_length=255)
    myfiles = models.FileField(upload_to="")

    def __str__(self):
        return str(self.user)
