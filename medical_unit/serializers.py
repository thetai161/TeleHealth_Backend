
from rest_framework import serializers
from .models import MedicalUnit
from authentication.models import User


class MedicalUnitSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user = User.objects.get(
                id=instance.user.id)
            email = user.email
            phone = user.phone
        except:
            email = ''
            phone = ''

        representation['email'] = email
        representation['phone'] = phone

        return representation
    class Meta:
        model = MedicalUnit
        fields = '__all__'



class PatientRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=5)
    username = serializers.CharField(max_length=255, min_length=3)
    phone = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    gender = serializers.CharField(max_length=20)
    ethnic = serializers.CharField(max_length=50)
    unsignedName = serializers.CharField(max_length=50)
    detail_address = serializers.CharField(max_length=255)
    dateOfBirth = serializers.DateField()
    insuranceCode = serializers.CharField(max_length=20)
    identification = serializers.CharField(max_length=20)
    contact = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=50)
    province = serializers.CharField(max_length=50)
    district = serializers.CharField(max_length=50)
    ward = serializers.CharField(max_length=50)

class MedicalUnitCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=5)
    username = serializers.CharField(max_length=255, min_length=3)
    phone = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    unsignedName = serializers.CharField(max_length=50)
    detail_address = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)    
    country = serializers.CharField(max_length=50)
    province = serializers.CharField(max_length=50)
    district = serializers.CharField(max_length=50)
    ward = serializers.CharField(max_length=50)