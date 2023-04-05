from django.shortcuts import render

# Create your views here.
from django.urls import path, include

from rest_framework import routers
from .views import MedicalUnitViewSet
router = routers.DefaultRouter()
router.register("", MedicalUnitViewSet, "medical_unit")

urlpatterns = [
    path('', include(router.urls)),
    path('detail_patient_by_medical_unit', MedicalUnitViewSet.as_view({
        'get': 'detailPatientByMedicalUnit'
    })),
    path('update_patient_by_medical_unit', MedicalUnitViewSet.as_view({
        'post': 'updatePatientByMedicalUnit'
    })),
    path('accept_doctor_wait_accept_by_medical_unit', MedicalUnitViewSet.as_view({
        'post': 'acceptDoctorWaitAcceptByMedicalUnit'
    })),
    path('delete_doctor_wait_accept_by_medical_unit', MedicalUnitViewSet.as_view({
        'post': 'deleteDoctorWaitAcceptByMedicalUnit'
    })),
    path('detail_medical_unit', MedicalUnitViewSet.as_view({
        'get': 'detailMedicalUnit'
    })),
]
