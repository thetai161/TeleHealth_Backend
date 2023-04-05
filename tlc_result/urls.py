from os import name
from django.contrib import admin
from django.urls import include, path
from .views import load_result


urlpatterns = [
    path('result/<int:id>/', load_result, name='load_result'),
]
