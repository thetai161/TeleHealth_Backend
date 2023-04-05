
from doctor.models import Doctor
from doctor.serializers import DoctorSerializer
from patient.models import Patient
from patient.serializers import PatientDetailSerializer
from rest_framework import serializers
from .models import PatientManagement
from authentication.models import User


class PatientManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientManagement
        fields = '__all__'

class PatientReadOnlyDoctorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            patient = Patient.objects.get(id=instance.patient.id)
            patientInfo = PatientDetailSerializer(patient).data
        except:
            patientInfo = ""

        representation['patient'] = patientInfo

        return representation

    class Meta:
        model = PatientManagement
        fields = '__all__'


class DoctorReadOnlyDoctorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            doctor = Doctor.objects.get(id=instance.doctor.id)
            doctorInfo = DoctorSerializer(doctor).data
            user = User.objects.get(id=doctor.user.id)
            doctorInfo['email'] = user.email
            doctorInfo['phone'] = user.phone
        except:
            doctorInfo = ""
        representation['doctor'] = doctorInfo

        return representation

    class Meta:
        model = PatientManagement
        fields = '__all__'
