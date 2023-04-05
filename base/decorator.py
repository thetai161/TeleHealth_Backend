from django.http import HttpResponse
from django.shortcuts import redirect, render

from base.message import error
from doctor.models import Doctor


def admin_only(view_func):
    def function(request, *args, **kwargs):
        roll = request.user.profile.is_admin
        if roll == True:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("Chức năng này chỉ dành cho Admin!")
    return function


def user_only(view_func):
    def function(request, *args, **kwargs):
        roll = request.user.profile.is_normal_user
        if roll == True:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("USER")
    return function


def doctor_accepted_only(view_func):
    def function(request, *args, **kwargs):
        doctor = Doctor.objects.get(user_id=request.user.id)
        if doctor.is_accept == True:
            return view_func(request, *args, **kwargs)
        else:
            return error(data="don't accept")
    return function
