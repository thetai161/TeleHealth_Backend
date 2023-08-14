from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from .models import Patient
from .serializers import PatientSerializer, PatientDetailSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from authentication.permissions import Role1, Role2, Role3, Role4


class PatientViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer
    permission_classes_by_action = {
        'list': [AllowAny],
        "destroy": [Role3],
    }

    @action(
        methods=["GET"],
        detail=False,
        url_path="detail_profile_patient"
    )
    def detailProfilePatient(self, request, *args, **kwargs):
        patient = Patient.objects.get(user_id=request.user.id)
        patientSerializer = PatientDetailSerializer(patient)
        return Response(data=patientSerializer.data, status=status.HTTP_200_OK)
