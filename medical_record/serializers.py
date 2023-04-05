
from rest_framework import serializers
from upload.models import File
from upload.serializers import FileSerializer
from .models import FileMedicalRecord, MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'


class FileMedicalRecordSerializer(serializers.ModelSerializer):
    file = FileSerializer()

    class Meta:
        model = FileMedicalRecord
        fields = '__all__'


class MedicalRecordReadOnlyPatientSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            fileMedicalRecords = FileMedicalRecord.objects.filter(
                medicalRecord_id=instance.id)
            files = FileMedicalRecordSerializer(
                fileMedicalRecords, many=True).data
        except:
            files = ""

        representation['files'] = files

        return representation

    class Meta:
        model = MedicalRecord
        fields = '__all__'


class UpdateMedicalRecordSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            fileMedicalRecords = FileMedicalRecord.objects.filter(
                medicalRecord_id=instance.id)
            files = FileMedicalRecordSerializer(
                fileMedicalRecords, many=True).data
        except:
            files = ""

        representation['files'] = files

        return representation

    class Meta:
        model = MedicalRecord
        exclude = ['creator', 'patient']
