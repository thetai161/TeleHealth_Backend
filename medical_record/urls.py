from django.shortcuts import render

# Create your views here.
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("", views.MedicalRecordViewSet, "medical_record")


urlpatterns = [
    path('', include(router.urls)),
    path('list_medical_record_by_patient_id', views.MedicalRecordViewSet.as_view({
        'get': 'list_medical_record_by_patientId'
    })),
    path('detail_medical_record', views.MedicalRecordViewSet.as_view({
        'get': 'detail_medical_record'
    })),
    path('delete_file_medical_record', views.MedicalRecordViewSet.as_view({
        'post': 'delete_file_medical_record'
    })),
    path('update_medical_record', views.MedicalRecordViewSet.as_view({
        'post': 'update_medical_record'
    })),
]
