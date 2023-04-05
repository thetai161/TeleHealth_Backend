from django.shortcuts import render

# Create your views here.
from django.urls import path, include

from rest_framework import routers
from . import views
from .views import NotificationViewSet

router = routers.DefaultRouter()
router.register("notification", views.NotificationViewSet, "notification")


urlpatterns = [
    path('', include(router.urls)),
    path('read_notification', NotificationViewSet.as_view({
        'post': 'readNotification'
    }))
]
