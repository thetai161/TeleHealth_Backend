from django.shortcuts import render
from address.models import Address
from doctor.models import Doctor
from doctor.serializers import DoctorSerializer
from .permissions import Role1, Role3
from rest_framework import generics, status, permissions
from .serializer import DoctorRegisterSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, ChangePasswordSerializer, GetUserReadOnlySerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

from .mixins import GetSerializerClassMixin
from base.message import success, error
from django.db import transaction

# Create your views here.


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            serializer.save()
            return success(data=serializer.data)
        return error(data=serializer.errors)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request.session['user_id'] = serializer.data['id']
                return success(data=serializer.data)
            return error("Sign in failed", data='')
        except:
            return error("Sign in failed", data='')


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success("Logout success", '')
            return error(data=serializer.errors)
        except:
            return error("Sign out failed", data='')


class Change_passwordAPIview(generics.GenericAPIView, GetSerializerClassMixin):

    serializer_class = ChangePasswordSerializer

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = request.user
                if not user.check_password(serializer.validated_data["old_password"]):
                    return error('old password is not correct', '')
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                serializer = GetUserReadOnlySerializer(user)
                return success(data=serializer.data)
            return error(data=serializer.errors)
        except:
            return error("Change password failed", data='')


class DoctorRegister(generics.GenericAPIView):
    serializer_class = DoctorRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            doctorData = request.data
            serializer = self.serializer_class(data=doctorData)
            if serializer.is_valid():
                user = User.objects.create_user(
                    email=doctorData['email'],
                    password=doctorData['password'],
                    username=doctorData['username'],
                    phone=doctorData['phone'],
                    role='role1',
                )
                doctorSerializer = RegisterSerializer(user)
                return success(data=doctorSerializer.data)
        except:
            return error("Failed", data='')


class PaymentAPIView(generics.GenericAPIView):

    def post(self, request):
        userId = request.data['userId']
        try:
            user = User.objects.get(id=userId)
            data = {
                'free_usage_count': user.free_usage_count,
                'unlimited_usage': user.unlimited_usage
            }
            return success(data=data)
        except Exception as ex:
            return error("Error", data=ex)


class SuccessPayment(generics.GenericAPIView):
    def post(self, request):
        userId = request.data['userId']
        try:
            user = User.objects.get(id=userId)
            user.unlimited_usage = True
            user.save()
            return success(data="ok")
        except Exception as ex:
            return error("Error", data=ex)