from django.shortcuts import get_object_or_404
from address.models import Address
from authentication.permissions import Role1, Role2, Role3, Role4
from authentication.serializer import RegisterSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from base.message import success, error

from authentication.models import User
from patient.models import Patient
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    serializer_action_classes = {
    }
    permission_classes_by_action = {
        'list': [AllowAny]
    }


    @action(
        methods=["GET"],
        detail=False,
        url_path="list_notification_for_user"
    )
    def listNotificationForUser(self, request):
        notification = Notification.objects.filter(user_id=request.user.id)[:10]
        notificationSerializer = NotificationSerializer(
            notification, many=True)
        return success(data=notificationSerializer.data)

    def readNotification(self, request):
        notificationId = self.request.GET.get('pk')
        notification = Notification.objects.get(id=notificationId)
        if notification.read == False:
            notification.read = True
            notification.save()
        return Response(data=notification.read, status=status.HTTP_200_OK)
