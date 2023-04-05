
from rest_framework import serializers
from .models import Doctor
from authentication.models import User
from address.models import Address
from address.serializers import AddressSerializer


class DoctorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user = User.objects.get(id=instance.user.id)
            doctorEmail = user.email
            doctorPhone = user.phone
            address = Address.objects.get(id=instance.address.id)
            doctorAddress = AddressSerializer(instance=address).data
        except:
            doctorEmail = ''
            doctorPhone = ''
            doctorAddress = ''

        representation['email'] = doctorEmail
        representation['phone'] = doctorPhone
        representation['address'] = doctorAddress

        return representation

    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15)
    country = serializers.CharField(max_length=40)
    province = serializers.CharField(max_length=40)
    district = serializers.CharField(max_length=40)
    ward = serializers.CharField(max_length=40)

    class Meta:
        model = Doctor
        exclude = ['user', 'is_accept']
