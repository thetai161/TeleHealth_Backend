from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
import django.contrib.auth.password_validation as validators
from django.utils.translation import gettext_lazy as _
from doctor.models import Doctor
from patient.models import Patient
from medical_unit.models import MedicalUnit


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, min_length=6, write_only=True)
    role = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'phone', 'role']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(
                'username includes both letters and numbers')
        return attrs

    def create(self, validated_data):
        print(validated_data)
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, required=False)
    tokens = serializers.SerializerMethodField()
    role = serializers.CharField(max_length=30, required=False)
    id = serializers.CharField(max_length=30, required=False)
    idProfile = serializers.CharField(max_length=30, required=False)

    def get_role(self, obj):
        user = User.objects.get(email=obj['email'])
        role = user.role
        return role

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
        return user.tokens()['access']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        # if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
        #     raise AuthenticationFailed(
        #         detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        # if not user.is_verified:
        #     raise AuthenticationFailed('Email is not verified')
        if user.role == 'role1':
            try:
                idProfile = Doctor.objects.get(user=user).id
            except:
                idProfile = None
        if user.role == 'role2':
            try:
                idProfile = Patient.objects.get(user=user).id
            except:
                idProfile = None
        if user.role == 'role3':
            try:
                idProfile = MedicalUnit.objects.get(user=user).id
            except:
                idProfile = None
        if user.role == 'role4':
            idProfile = None
        return {
            'email': user.email,
            'username': user.username,
            'role': user.role,
            'tokens': user.tokens,
            'id': user.id,
            'idProfile': idProfile

        }

        return super().validate(attrs)

    # class Meta:
    #     model = User
    #     fields = ['email', 'password', 'username', 'token']


class LogoutSerializer(serializers.ModelSerializer):

    refresh = serializers.CharField()

    default_error_messages = {
        'invalid': _('Bad Token')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('invalid')
        except:
            return "Token is expired or invalid"

    class Meta:
        model = User
        fields = ['refresh', 'tokens']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError(
                _("New password must be different from old password")
            )
        if data["confirm_password"] != data["new_password"]:
            raise serializers.ValidationError(
                _("The new password must be the same as the confirmation password")
            )

        try:
            validators.validate_password(password=data["new_password"])
        except Exception as e:
            raise serializers.ValidationError(e)

        return data


class GetUserReadOnlySerializer(serializers.Serializer):
    email = serializers.CharField(read_only=True)
    fullname = serializers.CharField(read_only=True)


class DoctorRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6)
    username = serializers.CharField(max_length=255, min_length=3)
    phone = serializers.CharField(max_length=20)
