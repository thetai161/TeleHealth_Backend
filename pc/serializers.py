
from doctor.models import Doctor
from doctor.serializers import DoctorSerializer
from patient.models import Patient
from patient.serializers import PatientDetailSerializer
from rest_framework import serializers
from .models import PcModel
from authentication.models import User


class PcSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcModel
        fields = '__all__'
