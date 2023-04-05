from django.shortcuts import render

# Create your views here.
from django.urls import path, include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("", views.PatientManagementViewSet, "patient_management")


urlpatterns = [
    path('', include(router.urls)),
    path('list_doctor_from_patient', views.PatientManagementViewSet.as_view({
        'get': 'listDoctorFromPatient'
    })),
    path('remove_patient_management', views.PatientManagementViewSet.as_view({
        'post': 'removePatientManagement'
    })),
    path('list_patient_by_doctor', views.PatientManagementViewSet.as_view({
        'get': 'listPatientByDoctor'
    })),
]
