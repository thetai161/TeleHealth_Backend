from django.contrib import admin

# Register your models here.
from .models import FileMedicalRecord, MedicalRecord


admin.site.register(MedicalRecord)
admin.site.register(FileMedicalRecord)