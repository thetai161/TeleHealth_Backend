from django.shortcuts import render

# Create your views here.
from django.urls import path, include

from rest_framework import routers
from .views import MeetingViewSet
router = routers.DefaultRouter()
router.register("", MeetingViewSet, "meeting")

urlpatterns = [
    path('', include(router.urls)),
    path('read_meeting', MeetingViewSet.as_view({
        'get': 'read'
    })),
    path('add_meeting_conclusion', MeetingViewSet.as_view({
        'post': 'addMeetingConclusion'
    })),
    path('add_meeting_conclusion_by_guest', MeetingViewSet.as_view({
        'post': 'addMeetingConclusionByGuest'
    }))
]
