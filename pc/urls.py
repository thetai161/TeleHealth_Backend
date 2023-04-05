from os import name
from django.contrib import admin
from django.urls import include, path
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", PcViewSet, "pc")

urlpatterns = [
    path('', include(router.urls)),

    path('pc_load', PcViewSet.as_view({
        'post': 'pc_load'
    })),
    path('get_result_by_patient_id', PcViewSet.as_view({
        'post': 'get_result_by_patient_id'
    })),
]
