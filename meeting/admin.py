from django.contrib import admin

# Register your models here.
from .models import Meeting, MeetingGuest


admin.site.register(Meeting)
admin.site.register(MeetingGuest)