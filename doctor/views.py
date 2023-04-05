from django.shortcuts import get_object_or_404
from address.models import Address
from authentication.permissions import Role1, Role2, Role3, Role4
from authentication.serializer import RegisterSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from .models import Doctor
from .serializers import DoctorSerializer, DoctorUpdateSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action


class DoctorViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Doctor.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorSerializer
    serializer_action_classes = {
        "update_profile_doctor": DoctorUpdateSerializer,
    }
    permission_classes_by_action = {
        'list': [AllowAny],
        "update_profile_doctor": [Role1],
    }

    @action(
        methods=["POST"],
        detail=False,
        url_path="update_profile_doctor"
    )
    def update_profile_doctor(self, request):
        user_id = request.user.id
        if user_id:
            try:
                doctor = Doctor.objects.get(user_id=user_id)
                address = Address.objects.create(
                    country=request.data['country'],
                    province=request.data['province'],
                    district=request.data['district'],
                    ward=request.data['ward']
                )
                request.data['address'] = address.id
                doctorSerializer = self.get_serializer(
                    instance=doctor, data=request.data, partial=True)
                doctorSerializer.is_valid(raise_exception=True)
                self.perform_update(doctorSerializer)
                user = User.objects.get(id=user_id)
                user.phone = request.data['phone']
                user.save()
                return success(data=doctorSerializer.data)
            except:
                address = Address.objects.create(
                    country=request.data['country'],
                    province=request.data['province'],
                    district=request.data['district'],
                    ward=request.data['ward']
                )
                doctor = Doctor.objects.create(
                    user_id=user_id,
                    name=request.data['name'],
                    gender=request.data['gender'],
                    detail_address=request.data['detail_address'],
                    unsignedName=request.data['unsignedName'],
                    medicalUnit_id=request.data['medicalUnit'],
                    address=address)
                doctorSerializer = DoctorSerializer(doctor)
                return success(data=doctorSerializer.data)

        else:
            raise Exception('not valid')

    def detailDoctor(self, request, *args, **kwargs):
        doctorId = self.request.GET.get('pk')
        doctor = Doctor.objects.get(id=doctorId)
        doctorSerializer = DoctorSerializer(doctor)
        return Response(data=doctorSerializer.data, status=status.HTTP_200_OK)
