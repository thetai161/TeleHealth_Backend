from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from upload.serializers import FileSerializer
from .models import FileMedicalRecord, MedicalRecord
from .serializers import MedicalRecordReadOnlyPatientSerializer, MedicalRecordSerializer, UpdateMedicalRecordSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from authentication.permissions import Role1, Role1or3, Role2, Role3, Role4


class MedicalRecordViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = MedicalRecord.objects.all()
    permission_classes = [Role1or3]
    serializer_class = MedicalRecordSerializer
    serializer_action_classes = {
        'detail_medical_record': MedicalRecordReadOnlyPatientSerializer,
        'update_medical_record': UpdateMedicalRecordSerializer,
    }
    permission_classes_by_action = {
        'list': [Role3],
        "create": [Role3],
    }

    def create(self, request):
        try:
            medicalRecordData = request.data
            medicalRecordData = medicalRecordData.dict()
            medicalRecordData['creator'] = str(request.user.id)
            medicalRecordSerializer = self.get_serializer(
                data=medicalRecordData)
            medicalRecordSerializer.is_valid(raise_exception=True)
            medicalRecord = medicalRecordSerializer.save()
            files = self.request.FILES.getlist('files', None)
            if files:
                for file in files:
                    data_file = {
                        'name': file.name,
                        'folder': 'medical_record',
                        'file': file,
                    }
                    image_serializer = FileSerializer(data=data_file)
                    image_serializer.is_valid(raise_exception=True)
                    file = image_serializer.save()
                    FileMedicalRecord.objects.create(
                        file_id=file.id, medicalRecord_id=medicalRecord.id)
            return success(data=medicalRecordSerializer.data)
        except:
            return error(data="data not valid")

    def list_medical_record_by_patientId(self, request, *args, **kwargs):
        patientId = self.request.GET.get('pk')
        medicalRecords = MedicalRecord.objects.filter(patient_id=patientId)
        medicalRecordsSerializer = self.get_serializer(
            medicalRecords, many=True)
        return success(data=medicalRecordsSerializer.data)

    def delete_file_medical_record(self, request, *args, **kwargs):
        try:
            fileMedicalRecordId = self.request.GET.get('pk')
            fileMedicalRecord = FileMedicalRecord.objects.get(
                id=fileMedicalRecordId)
            fileMedicalRecord.delete()
            return success(data='delete success!')
        except:
            return error(data='do not success')

    def detail_medical_record(self, request, *args, **kwargs):
        medicalRecordId = self.request.GET.get('pk')
        medicalRecord = MedicalRecord.objects.get(id=medicalRecordId)
        medicalRecordSerializer = self.get_serializer(medicalRecord)
        return success(data=medicalRecordSerializer.data)

    def update_medical_record(self, request, *args, **kwargs):
        try:
            medicalRecordId = self.request.GET.get('pk')
            medicalRecord = MedicalRecord.objects.get(id=medicalRecordId)
            medicalRecordSerializer = self.get_serializer(
                instance=medicalRecord, data=request.data)
            medicalRecordSerializer.is_valid(raise_exception=True)
            self.perform_update(medicalRecordSerializer)
            files = self.request.FILES.getlist('files', None)
            if files:
                for file in files:
                    data_file = {
                        'name': file.name,
                        'folder': 'medical_record',
                        'file': file,
                    }
                    image_serializer = FileSerializer(data=data_file)
                    image_serializer.is_valid(raise_exception=True)
                    file = image_serializer.save()
                    FileMedicalRecord.objects.create(
                        file_id=file.id, medicalRecord_id=medicalRecordId)
            medicalRecordSerializer = self.get_serializer(medicalRecord)
            return success(data=medicalRecordSerializer.data)
        except:
            return error('data not valid')
