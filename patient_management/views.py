from doctor.models import Doctor
from patient.serializers import PatientSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from .models import PatientManagement
from .serializers import DoctorReadOnlyDoctorSerializer, PatientManagementSerializer, PatientReadOnlyDoctorSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from authentication.permissions import Role1, Role2, Role3, Role4, Role1or3


class PatientManagementViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = PatientManagement.objects.all()
    permission_classes = [Role3]
    serializer_class = PatientManagementSerializer
    permission_classes_by_action = {
        'list': [AllowAny],
        "create": [Role3],
        "listPatientByDoctor": [Role1or3],
    }

    def listPatientByDoctor(self, request, *args, **kwargs):
        doctorId = self.request.GET.get('pk')
        doctor = Doctor.objects.get(id=doctorId)
        patients = PatientManagement.objects.filter(doctor=doctor)
        patientsSerializer = PatientReadOnlyDoctorSerializer(
            patients, many=True)
        return Response(data=patientsSerializer.data, status=status.HTTP_200_OK)

    def listDoctorFromPatient(self, request, *args, **kwargs):
        patientId = self.request.GET.get('pk')
        doctors = PatientManagement.objects.filter(patient_id=patientId)
        doctorsSerializer = DoctorReadOnlyDoctorSerializer(doctors, many=True)
        return Response(data=doctorsSerializer.data, status=status.HTTP_200_OK)

    def removePatientManagement(self, request, *args, **kwargs):
        id = self.request.GET.get('pk')
        patientManagement = PatientManagement.objects.get(id=id)
        patientManagement.delete()
        return success(data="delete success")
