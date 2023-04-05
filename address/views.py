from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.mixins import GetSerializerClassMixin
from .models import Address
from .serializers import AddressSerializer
from rest_framework import permissions


class AddressViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    permission_classes_by_action = {
        'list': [AllowAny],
        "create": [permissions.IsAuthenticated],
    }
