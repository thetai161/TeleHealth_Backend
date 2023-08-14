
from authentication.models import User
from rest_framework import serializers
from .models import Patient
from patient_management.models import PatientManagement
from address.models import Address
from address.serializers import AddressSerializer
from doctor.models import Doctor


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class DoctorIdPatientManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientManagement
        fields = '__all__'

class PatientDetailSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user = User.objects.get(id=instance.user.id)
            patientEmail = user.email
            patientPhone = user.phone
            if PatientManagement.objects.filter(patient_id=instance.id):
                patientManagement = True
                patientManagements = PatientManagement.objects.filter(patient_id=instance.id)
                patientManagementDoctorId = DoctorIdPatientManagementSerializer(instance=patientManagements, many=True).data
            else:
                patientManagement = False
                patientManagementDoctorId = ''
            address = Address.objects.get(id=instance.address.id)
            patientAddress = AddressSerializer(instance=address).data
        except:
            patientEmail = ''
            patientPhone = ''
            patientAddress = ''

        representation['email'] = patientEmail
        representation['phone'] = patientPhone
        representation['address'] = patientAddress
        representation['patientManagement'] = patientManagement
        representation['patientManagementDoctorId'] = patientManagementDoctorId

        return representation

    class Meta:
        model = Patient
        fields = '__all__'


class PatientUpdateByMedicalUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ['user', 'address', 'medicalUnit']