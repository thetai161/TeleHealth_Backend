from os import name
from django.contrib import admin
from django.urls import include, path
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", LoadFileViewSet, "load_file")

urlpatterns = [
    path('', include(router.urls)),

    path('get_result_by_patient_id', LoadFileViewSet.as_view({
        'get': 'get_result_by_patient_id'
    })),
    path('post_file', LoadFileViewSet.as_view({
        'post': 'post_file'
    })),
    path('detail_result', LoadFileViewSet.as_view({
        'get': 'detail_result'
    })),
]
